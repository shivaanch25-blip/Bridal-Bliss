import math
import re
from app.models import Product, Salon, BridalLook, Category, SalonService

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) in kilometers.
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers.
    return c * r

def tag_similarity(tags1, tags2):
    """
    Computes Jaccard Similarity between two comma-separated tag strings.
    """
    if not tags1 or not tags2:
        return 0.0
    set1 = {t.strip().lower() for t in tags1.split(',') if t.strip()}
    set2 = {t.strip().lower() for t in tags2.split(',') if t.strip()}
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def get_hybrid_product_recommendations(user_pref=None, look=None, limit=6):
    """
    Recommends products matching user preferences and selected bridal look.
    Uses similarity matching on style tags, colors, and budget tier.
    """
    query = Product.query
    all_products = query.all()
    
    # Compile matching tags
    target_tags = []
    preferred_colors = []
    target_budget_tier = 'midrange'
    
    if user_pref:
        if user_pref.jewelry_style:
            target_tags.append(user_pref.jewelry_style)
        if user_pref.wedding_theme:
            target_tags.extend(user_pref.wedding_theme.split())
        if user_pref.preferred_colors:
            preferred_colors = [c.strip().lower() for c in user_pref.preferred_colors.split(',')]
            target_tags.extend(preferred_colors)
        if user_pref.budget:
            # Map budget to product tier
            if user_pref.budget < 100000:
                target_budget_tier = 'budget'
            elif user_pref.budget > 300000:
                target_budget_tier = 'luxury'
            else:
                target_budget_tier = 'midrange'

    if look:
        if look.theme_tags:
            target_tags.extend(look.theme_tags.split(','))
        if look.color_palette:
            colors = [c.strip().lower() for c in look.color_palette.split(',')]
            preferred_colors.extend(colors)
            target_tags.extend(colors)
            
    target_tags_str = ",".join(target_tags)
    scored_products = []
    
    for p in all_products:
        # Base Jaccard similarity score
        tag_score = tag_similarity(target_tags_str, p.style_tags)
        
        # Color match boost
        color_match = 0
        if preferred_colors and p.style_tags:
            p_tags_set = {t.strip().lower() for t in p.style_tags.split(',')}
            for color in preferred_colors:
                if color in p_tags_set:
                    color_match += 0.25
        
        # Budget alignment score
        budget_score = 1.0 if p.budget_tier == target_budget_tier else 0.5
        
        # Total matching score
        final_score = (tag_score * 0.5) + (color_match * 0.25) + (budget_score * 0.25)
        
        scored_products.append((p, final_score))
        
    # Sort descending
    scored_products.sort(key=lambda x: x[1], reverse=True)
    return [item[0] for item in scored_products[:limit]]

def get_recommended_salons(user_lat, user_lon, look=None, max_distance=50, limit=5):
    """
    Ranks salons by proximity, capabilities (matching look makeup/hair style),
    rating, and average service price tier.
    """
    salons = Salon.query.filter_by(is_approved=True).all()
    scored_salons = []
    
    target_style = ""
    if look:
        target_style = (look.makeup_style or "") + " " + (look.hairstyle or "")
    target_style = target_style.lower()
    
    for salon in salons:
        # Calculate distance
        dist = haversine_distance(user_lat, user_lon, salon.latitude, salon.longitude)
        if dist > max_distance:
            continue
            
        # Distance score (closer is better, max score of 1.0)
        dist_score = max(0.0, 1.0 - (dist / max_distance))
        
        # Rating score
        rating_score = (salon.rating / 5.0) if salon.rating else 0.8
        
        # Capability Match
        capability_score = 0.5
        for service in salon.services:
            if service.service_name.lower() in target_style or any(word in service.service_name.lower() for word in target_style.split()):
                capability_score = 1.0
                break
                
        # Total Utility Rank score
        rank_score = (dist_score * 0.4) + (rating_score * 0.3) + (capability_score * 0.3)
        scored_salons.append((salon, dist, rank_score))
        
    scored_salons.sort(key=lambda x: x[2], reverse=True)
    return [(item[0], item[1]) for item in scored_salons[:limit]]

def format_budget_plan(total_budget):
    """
    Allocates budget into packages based on percentages.
    """
    return {
        "total": total_budget,
        "dress": total_budget * 0.40,      # 40% for dresses
        "jewelry": total_budget * 0.30,    # 30% for jewelry
        "makeup": total_budget * 0.15,     # 15% for salons/makeup artist
        "accessories": total_budget * 0.075,# 7.5% for clutches, hair, footwear
        "emergency": total_budget * 0.075   # 7.5% emergency buffer
    }

class BridalChatbot:
    """
    Context-aware keyword chatbot assistant.
    Queries active models to return real recommendations.
    """
    def __init__(self, user=None):
        self.user = user

    def respond(self, message):
        msg = message.lower().strip()
        
        # 1. Budget Plan question
        if "budget" in msg or "cost" in msg or "plan" in msg:
            nums = re.findall(r'\d[\d,\s]*', msg)
            if nums:
                # Extract numerical value
                num_str = re.sub(r'[\s,]', '', nums[0])
                try:
                    val = float(num_str)
                    if val < 5000: # Could be budget under salon search
                        pass
                    else:
                        alloc = format_budget_plan(val)
                        return f"Here is a premium wedding budget plan for **₹{val:,.2f}**:<br>" \
                               f"- 👗 **Bridal Outfits (40%)**: ₹{alloc['dress']:,.2f}<br>" \
                               f"- 💎 **Jewelry (30%)**: ₹{alloc['jewelry']:,.2f}<br>" \
                               f"- 💄 **Makeup & Styling (15%)**: ₹{alloc['makeup']:,.2f}<br>" \
                               f"- 👠 **Accessories (7.5%)**: ₹{alloc['accessories']:,.2f}<br>" \
                               f"- 🚨 **Emergency Buffer (7.5%)**: ₹{alloc['emergency']:,.2f}<br><br>" \
                               f"I have saved this plan to your profile! You can explore items fitting these brackets in our Shop."
                except ValueError:
                    pass
            
            if self.user and self.user.budget_plan:
                plan = self.user.budget_plan
                return f"Your current planned budget is **₹{plan.total_budget:,.2f}**:<br>" \
                       f"- Outfits: ₹{plan.dress_budget:,.2f}<br>" \
                       f"- Jewelry: ₹{plan.jewelry_budget:,.2f}<br>" \
                       f"- Makeup: ₹{plan.makeup_budget:,.2f}<br>" \
                       f"- Accessories: ₹{plan.accessories_budget:,.2f}<br>" \
                       f"- Buffer: ₹{plan.emergency_budget:,.2f}"
            
            return "To plan your budget, tell me something like: 'Help me plan a budget of 200000' or 'Calculate styling costs for 150000'."

        # 2. Look suggestion / Face Shape / Skin Tone
        if any(w in msg for w in ["look", "style", "makeup", "suit"]):
            if "skin" in msg or "tone" in msg or "fair" in msg or "medium" in msg or "dusk" in msg or "deep" in msg:
                # Suggest looks matching skin tone
                tone = "warm"
                if "fair" in msg: tone = "fair"
                elif "dusk" in msg: tone = "dusky"
                elif "deep" in msg: tone = "deep"
                
                looks = BridalLook.query.filter(BridalLook.color_palette.like(f"%{tone}%") | BridalLook.theme_tags.like(f"%{tone}%")).all()
                if not looks:
                    looks = BridalLook.query.limit(2).all()
                
                response = f"For a **{tone.capitalize()}** skin tone, here are some elegant bridal looks:<br>"
                for l in looks:
                    response += f"- **[{l.name}](/studio/look/{l.id})**: Palette: {l.color_palette}. Style: {l.makeup_style}<br>"
                return response
            
            if "round" in msg or "oval" in msg or "heart" in msg or "square" in msg:
                shape = "oval"
                for s in ["round", "oval", "heart", "square"]:
                    if s in msg: shape = s
                
                return f"For an **{shape.capitalize()}** face shape, we recommend hairstyles with soft face-framing tendrils or a sophisticated high bun to elevate the silhouette. Our **Royal Rajput** and **Modern Luxury** presets match these recommendations beautifully!"

            # General look list
            looks = BridalLook.query.limit(3).all()
            response = "Here are some of our trending AI Bridal Looks:<br>"
            for l in looks:
                response += f"- **[{l.name}](/studio/look/{l.id})** ({l.makeup_style})<br>"
            return response + "You can select a look to find matching outfit details and salons!"

        # 3. Salon under budget
        if "salon" in msg or "parlor" in msg or "artist" in msg:
            nums = re.findall(r'\d[\d,\s]*', msg)
            max_price = None
            if nums:
                try:
                    max_price = float(re.sub(r'[\s,]', '', nums[0]))
                except ValueError:
                    pass
            
            if max_price:
                # Filter salons with services under max_price
                services = SalonService.query.filter(SalonService.price <= max_price).limit(3).all()
                if services:
                    res = f"Here are salons offering bridal services under **₹{max_price:,.2f}**:<br>"
                    for s in services:
                        res += f"- **[{s.salon.name}](/salons/{s.salon_id})** in {s.salon.city}: *{s.service_name}* for **₹{s.price:,.2f}**<br>"
                    return res
                else:
                    return f"I couldn't find specific services below ₹{max_price:,.2f}, but you can browse all approved [salons](/salons) to contact them for quotes!"
            
            # General salon queries
            salons = Salon.query.filter_by(is_approved=True).limit(3).all()
            res = "Here are some top-rated salons on our platform:<br>"
            for s in salons:
                res += f"- **[{s.name}](/salons/{s.id})** in {s.city} (Rating: ⭐{s.rating}, Contact: {s.contact_number})<br>"
            return res + "You can search by city or pincode on the [Salon Finder](/salons) page."

        # 4. Jewelry and outfits
        if "jewelry" in msg or "neck" in msg or "lehenga" in msg or "saree" in msg or "dress" in msg:
            color = ""
            for c in ["red", "pink", "maroon", "gold", "ivory", "pastel", "green"]:
                if c in msg:
                    color = c
            
            if color:
                products = Product.query.filter(Product.style_tags.like(f"%{color}%")).limit(3).all()
                if products:
                    res = f"Here are matching products themed with **{color.capitalize()}**:<br>"
                    for p in products:
                        res += f"- **[{p.name}](/shop/product/{p.id})** (Price: ₹{p.price:,.2f})<br>"
                    return res
            
            # Default response
            products = Product.query.filter(Product.category_id.in_([1, 2])).limit(3).all() # Dresses / Jewelry
            res = "Take a look at these popular items from our collections:<br>"
            for p in products:
                res += f"- **[{p.name}](/shop/product/{p.id})** (Price: ₹{p.price:,.2f})<br>"
            return res + "You can search more in our full [Shopping Catalog](/shop)."

        # 5. Default fallback
        return "I am your Bridal Bliss Stylist. I can help you:<br>" \
               "- Build a personalized **budget plan** (e.g., 'plan a budget of 300000')<br>" \
               "- Recommend **bridal looks** (e.g., 'What look matches dusky skin tone?')<br>" \
               "- Find **salons & services** under a price limit (e.g., 'find salon under 15000')<br>" \
               "- Recommend matching **jewelry or outfits**."

import os
from app import create_app
from app.models import db, User, Category, Product, BridalLook, LookReview, Salon, SalonService, SalonPortfolio, Wishlist, BudgetPlan

def seed_db():
    app = create_app()
    with app.app_context():
        # Drop and recreate tables
        db.drop_all()
        db.create_all()
        print("Database tables recreated successfully.")

        # 1. Create Core Users
        admin = User(username='admin', email='admin@bridalbliss.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        bride = User(username='priya', email='priya@gmail.com', role='bride')
        bride.set_password('priya123')
        db.session.add(bride)

        # Salon owners
        owner1 = User(username='anaya_salons', email='anaya@salon.com', role='salon_owner')
        owner1.set_password('anaya123')
        db.session.add(owner1)

        owner2 = User(username='royal_salons', email='royal@salon.com', role='salon_owner')
        owner2.set_password('royal123')
        db.session.add(owner2)

        owner3 = User(username='vogue_salons', email='vogue@salon.com', role='salon_owner')
        owner3.set_password('vogue123')
        db.session.add(owner3)

        db.session.commit()
        print("Core users seeded.")

        # 2. Create Categories
        cat_dresses = Category(name='Dresses')
        cat_jewelry = Category(name='Jewelry')
        cat_makeup = Category(name='Makeup Kits')
        cat_accessories = Category(name='Accessories')
        db.session.add_all([cat_dresses, cat_jewelry, cat_makeup, cat_accessories])
        db.session.commit()

        # Subcategories
        sub_lehenga = Category(name='Lehenga', parent_id=cat_dresses.id)
        sub_saree = Category(name='Saree', parent_id=cat_dresses.id)
        sub_gown = Category(name='Gown', parent_id=cat_dresses.id)
        sub_reception = Category(name='Reception Dress', parent_id=cat_dresses.id)

        sub_necklace = Category(name='Necklace', parent_id=cat_jewelry.id)
        sub_earrings = Category(name='Earrings', parent_id=cat_jewelry.id)
        sub_bangles = Category(name='Bangles', parent_id=cat_jewelry.id)
        sub_maang = Category(name='Maang Tikka', parent_id=cat_jewelry.id)

        sub_found = Category(name='Foundation', parent_id=cat_makeup.id)
        sub_lipstick = Category(name='Lipstick', parent_id=cat_makeup.id)
        sub_eyeshadow = Category(name='Eyeshadow', parent_id=cat_makeup.id)
        sub_pkg = Category(name='Bridal Makeup Packages', parent_id=cat_makeup.id)

        sub_foot = Category(name='Footwear', parent_id=cat_accessories.id)
        sub_clutch = Category(name='Clutches', parent_id=cat_accessories.id)
        sub_hairacc = Category(name='Hair Accessories', parent_id=cat_accessories.id)

        db.session.add_all([
            sub_lehenga, sub_saree, sub_gown, sub_reception,
            sub_necklace, sub_earrings, sub_bangles, sub_maang,
            sub_found, sub_lipstick, sub_eyeshadow, sub_pkg,
            sub_foot, sub_clutch, sub_hairacc
        ])
        db.session.commit()
        print("Categories and subcategories seeded.")

        # 3. Create Products
        p1 = Product(
            name='Royal Crimson Velvet Lehenga',
            description='Exquisite hand-embroidered Zardosi velvet lehenga set, featuring intricate gold floral motifs and an ivory organza dupatta.',
            price=125000.0,
            category_id=sub_lehenga.id,
            image_url='https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80',
            budget_tier='luxury',
            style_tags='rajput, traditional, red, gold, heavy'
        )
        p2 = Product(
            name='Emerald Kundan Choker Set',
            description='A stunning handcrafted 22k gold plated kundan necklace with layered green beads, matching earrings, and maang tikka.',
            price=4500.0,
            category_id=sub_necklace.id,
            image_url='https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80',
            budget_tier='luxury',
            style_tags='traditional, gold, emerald, kundan, heavy'
        )
        p3 = Product(
            name='Blush Pink Silk Banarasi Saree',
            description='Traditional handwoven pure silk Banarasi saree with gold zari border, perfect for wedding rituals or receptions.',
            price=24000.0,
            category_id=sub_saree.id,
            image_url='https://images.unsplash.com/photo-1610030470298-40b355e717ee?auto=format&fit=crop&w=600&q=80',
            budget_tier='midrange',
            style_tags='bengali, traditional, pink, gold, minimalist'
        )
        p4 = Product(
            name='Matte Liquid Lipstick Trio',
            description='Bridal bliss exclusive set of three long-lasting liquid lipsticks in Classic Crimson, Dust Rose, and Peachy Nude.',
            price=1800.0,
            category_id=sub_lipstick.id,
            image_url='https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=600&q=80',
            budget_tier='budget',
            style_tags='makeup, pink, red, nude, dewy, matte'
        )
        p5 = Product(
            name='Classic Ivory Bridal Heels',
            description='Comfortable block heels wrapped in premium ivory silk satin with delicate pearl and bead embellishments.',
            price=5500.0,
            category_id=sub_foot.id,
            image_url='https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=600&q=80',
            budget_tier='midrange',
            style_tags='accessories, footwear, ivory, white, minimalist'
        )
        p6 = Product(
            name='Gold Plated Kundan Kada Bangles',
            description='Set of 2 royal kada bangles featuring fine kundan stone settings and intricate red enamel work.',
            price=12000.0,
            category_id=sub_bangles.id,
            image_url='https://images.unsplash.com/photo-1601121141461-9d6647bca1ed?auto=format&fit=crop&w=600&q=80',
            budget_tier='midrange',
            style_tags='traditional, gujarati, rajput, gold, kundan'
        )
        p7 = Product(
            name='Champagne Sequin Reception Gown',
            description='Elegant slim-fit gown with hand-sewn shimmer sequins, a trailing drape, and a modern off-shoulder silhouette.',
            price=68000.0,
            category_id=sub_gown.id,
            image_url='https://images.unsplash.com/photo-1595777457583-95e059d581b8?auto=format&fit=crop&w=600&q=80',
            budget_tier='luxury',
            style_tags='modern, luxury, champagne, rose gold, shimmer'
        )
        p8 = Product(
            name='Kanjeevaram Temple Saree',
            description='Glorious mustard yellow and maroon border silk saree decorated with traditional temple carvings motifs in gold thread.',
            price=38000.0,
            category_id=sub_saree.id,
            image_url='https://images.unsplash.com/photo-1610030469668-93535c17b6b3?auto=format&fit=crop&w=600&q=80',
            budget_tier='luxury',
            style_tags='south indian, traditional, yellow, red, gold'
        )
        p9 = Product(
            name='Temple Pearl Jhumkas',
            description='Intricately crafted temple style earrings showing Goddess Lakshmi motifs, drop pearls, and ruby details.',
            price=8500.0,
            category_id=sub_earrings.id,
            image_url='https://images.unsplash.com/photo-1635767798638-3e25273a8236?auto=format&fit=crop&w=600&q=80',
            budget_tier='budget',
            style_tags='south indian, traditional, gold, pearl, ruby'
        )
        p10 = Product(
            name='Bridal HD Glow Foundation Kit',
            description='Waterproof professional HD foundation palette that offers flawless matte-finish camera coverage for all skin tones.',
            price=4200.0,
            category_id=sub_found.id,
            image_url='https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=600&q=80',
            budget_tier='budget',
            style_tags='makeup, foundation, dewy, matte'
        )
        p11 = Product(
            name='Embellished Rose Gold Clutch',
            description='Luxury hardcase bridal clutch featuring rose gold metallic frame, fine bead embroidery, and detachable chain.',
            price=4800.0,
            category_id=sub_clutch.id,
            image_url='https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=600&q=80',
            budget_tier='midrange',
            style_tags='accessories, rose gold, modern, luxury'
        )
        p12 = Product(
            name='Gota Patti Sheesphool / Maang Tikka',
            description='Traditional Rajasthani mathapatti featuring gota patti ribbon work and tiny pearls.',
            price=3500.0,
            category_id=sub_maang.id,
            image_url='https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?auto=format&fit=crop&w=600&q=80',
            budget_tier='budget',
            style_tags='rajput, traditional, gold, pearl, gotapatti'
        )

        db.session.add_all([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12])
        db.session.commit()
        print("Catalog products seeded.")

        # 4. Create Bridal Looks
        look_gujarati = BridalLook(
            name='Traditional Gujarati Bride',
            makeup_style='Soft Dewy Makeup, Bold Kohl Rimmed Eyes, Red Lip Tint',
            hairstyle='Classic Low Bun Wrapped in Mogra Gajra',
            jewelry_style='Kundan Choker, Heavy Jhumkas, Traditional Damani Maang Tikka, Red & Gold Glass Glass Bangles',
            outfit_style='Red and White Gharchola Saree or Panetar Lehenga with Gota Patti Border',
            color_palette='Red, White, Green, Gold, Warm Dewy',
            description='The timeless elegance of a Gujarati bride, radiating tradition in a Panetar or Gharchola saree, featuring majestic kundan ornaments and a gajra bun.',
            image_url='/static/images/looks/gujarati.jpg',
            theme_tags='gujarati, traditional, red, white, gold, warm'
        )
        look_rajput = BridalLook(
            name='Royal Rajput Bride',
            makeup_style='Rich Matte Base, Smokey Metallic Eyes, Regal Deep Crimson Lipstick',
            hairstyle='Center Partitioned Bun with Bajuband & Dupatta Draping',
            jewelry_style='Aad Choker Necklace, Rakhdi / Borla, Bajuband, Heavy Hathpan',
            outfit_style='Heavy Silk Poshak with Zardosi Embroidery and Kundan borders',
            color_palette='Crimson, Gold, Emerald, Royal Red',
            description='Channel royal Rajasthani heritage with a magnificent Rajput Poshak, complete with a traditional Borla (maang tikka) and a majestic Rajput Aad collar.',
            image_url='/static/images/looks/rajput.jpg',
            theme_tags='rajput, traditional, red, gold, heavy'
        )
        look_south = BridalLook(
            name='South Indian Bride',
            makeup_style='Bright Flawless Matte Base, Soft Coral Blushing, Gold Eye Pigment',
            hairstyle='Elaborate Long Hair Braid (Jada) decorated with Net Gajra and Kemp clips',
            jewelry_style='22k Gold Temple jewelry set, Laxmi Coin Haram, Manga Malai, Ottiyanam (waist belt)',
            outfit_style='Authentic Kanjeevaram Silk Saree in Red and Golden zari',
            color_palette='Mustard Yellow, Deep Red, Gold, Olive Green',
            description='Embody South Indian temple grace wearing a glowing Kanjeevaram saree, adorned with sacred kemp temple jewelry and a majestic flower-braid (Jada).',
            image_url='/static/images/looks/south_indian.jpg',
            theme_tags='south indian, traditional, gold, red'
        )
        look_bengali = BridalLook(
            name='Bengali Bride',
            makeup_style='Flawless Fair Highlighted Base, Winged Eyeliner, Chandan patterns on Forehead, Red Bindi',
            hairstyle='Traditional Bun crowned with white Mukut / Crown',
            jewelry_style='Gold Sita Har, Jhumkas, Tikli, Shakha and Pola bangles',
            outfit_style='Bright Red Banarasi Silk Saree draped in traditional Bengali Aathpourey style',
            color_palette='Red, White, Gold, Crimson, Fair',
            description='Capture Bengali wedding romance with custom forehead Chandan artwork, traditional red-and-white Shakha-Pola bangles, and a bright red Banarasi saree.',
            image_url='/static/images/looks/bengali.jpg',
            theme_tags='bengali, traditional, red, white, gold, fair'
        )
        look_minimal = BridalLook(
            name='Minimalist Bride',
            makeup_style='Clean Glass Skin Makeup, Soft Pink Blush, Nude Gloss Lips',
            hairstyle='Soft Loose Waves or half-up-half-down floral hair styling',
            jewelry_style='Dainty Diamond Pendant, matching diamond studs, and simple Platinum bracelets',
            outfit_style='Lightweight Pastel Pink or Peach Organza Lehenga',
            color_palette='Pastel Pink, Peach, Ivory, Nude, Mint Green',
            description='An elegant selection for the modern bride who loves simplicity: light pastel hues, dewy nude makeup, and delicate, sparkly diamonds.',
            image_url='/static/images/looks/minimalist.jpg',
            theme_tags='minimalist, modern, pink, ivory, pastel, nude'
        )
        look_luxury = BridalLook(
            name='Modern Luxury Bride',
            makeup_style='Sultry Bronze Eyes, Sculpted Contour Base, Shimmer Highlights, Peach Nude lips',
            hairstyle='Polished sleek ponytail or side sweep Hollywood waves',
            jewelry_style='Statement Diamond Choker and cuff bangles',
            outfit_style='Contemporary Rose Gold or Champagne Sequin Gown with train',
            color_palette='Champagne, Rose Gold, Silver, Shimmer, Bronze',
            description='Exude ultimate opulence on your reception evening in a glittering metallic gown, sculpted Hollywood waves, and luxury diamond jewelry.',
            image_url='/static/images/looks/luxury.jpg',
            theme_tags='modern, luxury, rose gold, champagne, shimmer, bronze'
        )
        look_celeb = BridalLook(
            name='Celebrity Inspired Bride',
            makeup_style='Dewy Glass Skin, Subtle Rose gold Smokey eyes, Velvet Dusty Rose lips',
            hairstyle='Middle-parted sleek low bun with a light sheer veil covering',
            jewelry_style='Uncut Polki diamond necklace, heavy emerald drops, and sleek Mathapatti',
            outfit_style='Blush Pink or Peach Georgette Lehenga with sequin embroidery',
            color_palette='Blush Pink, Peach, Emerald, Sage Green, Beige',
            description='Recreate the iconic, dreamy Bollywood celebrity wedding look with soft pastel lehengas, Polki chokers, and fresh, natural dewy makeup.',
            image_url='/static/images/looks/celebrity.jpg',
            theme_tags='celebrity, modern, pink, emerald, dewy'
        )

        db.session.add_all([
            look_gujarati, look_rajput, look_south, 
            look_bengali, look_minimal, look_luxury, look_celeb
        ])
        db.session.commit()
        print("Bridal Looks seeded.")

        # Add initial review for looks
        r_look1 = LookReview(user_id=bride.id, look_id=look_gujarati.id, rating=5, comment="Absolutely gorgeous! The red and white color coordination is perfect for traditional Gujarati weddings.")
        db.session.add(r_look1)
        db.session.commit()

        # 5. Create Salons (specifically focusing on Gujarat cities + major metros)
        # Coordinates (latitude, longitude):
        # Vadodara: 22.3072, 73.1812
        # Ahmedabad: 23.0225, 72.5714
        # Surat: 21.1702, 72.8311
        # Rajkot: 22.3039, 70.8022
        # Mumbai: 19.0760, 72.8777
        # Delhi: 28.6139, 77.2090
        # Bangalore: 12.9716, 77.5946
        
        s1 = Salon(
            name='Anaya Bridal Artistry & Makeovers',
            description='Award-winning luxury bridal boutique specializing in Traditional Gujarati and Royal Rajput makeup, draping, and luxury styling. Led by celebrity makeup designer Anaya.',
            contact_number='+91 98765 43210',
            address='302, Alkapuri Arcade, RC Dutt Road, Alkapuri',
            city='Vadodara',
            state='Gujarat',
            pincode='390007',
            rating=4.9,
            experience_years=12,
            latitude=22.3112,
            longitude=73.1754,
            is_approved=True,
            owner_id=owner1.id
        )
        s2 = Salon(
            name='Royal Rajput Heritage Salon',
            description='Specialized makeover parlor based in Ahmedabad, providing heavy royal poshak styling, Borla placements, and traditional bridal matte makeup.',
            contact_number='+91 98765 43211',
            address='101, Satved Complex, CG Road',
            city='Ahmedabad',
            state='Gujarat',
            pincode='380009',
            rating=4.8,
            experience_years=15,
            latitude=23.0250,
            longitude=72.5680,
            is_approved=True,
            owner_id=owner2.id
        )
        s3 = Salon(
            name='Marigold Bridal Makeovers',
            description='Premium beauty parlor in Surat focusing on wedding hairstyles, luxury glass skin makeovers, and custom saree/lehenga dupatta draping.',
            contact_number='+91 98765 43212',
            address='G-5, Shringar Heritage, Vesu Char Rasta, Vesu',
            city='Surat',
            state='Gujarat',
            pincode='395007',
            rating=4.7,
            experience_years=8,
            latitude=21.1512,
            longitude=72.7932,
            is_approved=True,
            owner_id=owner3.id
        )
        s4 = Salon(
            name='Shree Makeup & Hair Studio',
            description='Well-known bridal studio in Rajkot. We create customizable styles ranging from traditional Gujarati panetar drapes to modern sleek reception hairdos.',
            contact_number='+91 98765 43213',
            address='Nirmala Convent Road, opposite Patel Kanya Chhatralaya',
            city='Rajkot',
            state='Gujarat',
            pincode='360007',
            rating=4.6,
            experience_years=6,
            latitude=22.2980,
            longitude=70.7915,
            is_approved=True,
            owner_id=owner1.id
        )
        s5 = Salon(
            name='Vogue Elegance & Bridal Spa',
            description='Metropolitan celebrity bridal lounge in Bandra, Mumbai. We provide high-end airbrush makeup, celebrity-inspired pastel looks, and diamond jewelry pairing sessions.',
            contact_number='+91 99999 88888',
            address='Turner Road, Near Bandra Station, Bandra West',
            city='Mumbai',
            state='Maharashtra',
            pincode='400050',
            rating=4.9,
            experience_years=14,
            latitude=19.0596,
            longitude=72.8295,
            is_approved=True,
            owner_id=owner3.id
        )
        s6 = Salon(
            name='Ambika Pillai Luxury Makeovers',
            description='High-end designer salon chain in Connaught Place, New Delhi. Famous for luxury destination weddings and modern glass-skin makeup styles.',
            contact_number='+91 99999 11111',
            address='Outer Circle, Connaught Place',
            city='Delhi',
            state='NCR',
            pincode='110001',
            rating=4.9,
            experience_years=20,
            latitude=28.6304,
            longitude=77.2177,
            is_approved=True,
            owner_id=owner2.id
        )
        s7 = Salon(
            name='Shringar Bridal Spa & Temple Glow',
            description='Specialists in South Indian Bridal makeups, elaborate Jada hair braiding, and matching traditional kemp jewelry settings.',
            contact_number='+91 99999 22222',
            address='12th Main Road, Indiranagar',
            city='Bangalore',
            state='Karnataka',
            pincode='560038',
            rating=4.8,
            experience_years=10,
            latitude=12.9784,
            longitude=77.6408,
            is_approved=True,
            owner_id=owner1.id
        )
        
        # Adding a pending salon for admin approvals testing
        s_pending = Salon(
            name='Dazzle Beauty Zone (Pending)',
            description='New bridal salon in Vadodara looking to register and offer budget-friendly makeup services.',
            contact_number='+91 99999 33333',
            address='Bhimnath Mahadev Temple Road, Sayajiganj',
            city='Vadodara',
            state='Gujarat',
            pincode='390002',
            rating=4.0,
            experience_years=3,
            latitude=22.3166,
            longitude=73.1892,
            is_approved=False,
            owner_id=owner3.id
        )

        db.session.add_all([s1, s2, s3, s4, s5, s6, s7, s_pending])
        db.session.commit()
        print("Salons seeded.")

        # 6. Add services for Salons
        services = [
            # Salon 1 (Vadodara)
            SalonService(salon_id=s1.id, service_name='Premium Bridal Airbrush Makeup & Draping', price=25000.0, category='makeup'),
            SalonService(salon_id=s1.id, service_name='Traditional Gujarati Panetar Hair Bun & Gajra Styling', price=6000.0, category='hair'),
            SalonService(salon_id=s1.id, service_name='Bridal Jewelry Setting & Dupatta Pinning', price=2500.0, category='styling'),
            # Salon 2 (Ahmedabad)
            SalonService(salon_id=s2.id, service_name='Royal Rajput Matte Bridal Makeover', price=32000.0, category='makeup'),
            SalonService(salon_id=s2.id, service_name='Heavy Rajput Borla & Dupatta Styling', price=5000.0, category='styling'),
            # Salon 3 (Surat)
            SalonService(salon_id=s3.id, service_name='HD Glow Bridal Face Makeup', price=18000.0, category='makeup'),
            SalonService(salon_id=s3.id, service_name='Elegant Reception Waves & Floral Twists', price=4500.0, category='hair'),
            # Salon 4 (Rajkot)
            SalonService(salon_id=s4.id, service_name='Gujarati Bridal Makeover (Basic)', price=12000.0, category='makeup'),
            SalonService(salon_id=s4.id, service_name='Simple Saree Pleating & Draping', price=1500.0, category='styling'),
            # Salon 5 (Mumbai)
            SalonService(salon_id=s5.id, service_name='Celebrity Glass Skin HD Bridal Makeover', price=45000.0, category='makeup'),
            SalonService(salon_id=s5.id, service_name='Hollywood Waves Styling & Extensions', price=12000.0, category='hair'),
            # Salon 6 (Delhi)
            SalonService(salon_id=s6.id, service_name='Destination Signature Bridal Makeup', price=60000.0, category='makeup'),
            # Salon 7 (Bangalore)
            SalonService(salon_id=s7.id, service_name='Traditional South Indian Temple Makeup', price=22000.0, category='makeup'),
            SalonService(salon_id=s7.id, service_name='Full Length Flower Jada Braiding', price=8000.0, category='hair')
        ]
        db.session.add_all(services)
        db.session.commit()
        print("Salon services seeded.")

        # 7. Add Portfolios (Before/After descriptions)
        portfolios = [
            SalonPortfolio(salon_id=s1.id, before_image_url='/static/images/portfolio/s1_b.jpg', after_image_url='/static/images/portfolio/s1_a.jpg', description='Traditional Gujarati panetar transformation with kundan jewelry setting.'),
            SalonPortfolio(salon_id=s2.id, before_image_url='/static/images/portfolio/s2_b.jpg', after_image_url='/static/images/portfolio/s2_a.jpg', description='Royal Rajput poshak makeover with signature crimson lips.'),
            SalonPortfolio(salon_id=s5.id, before_image_url='/static/images/portfolio/s5_b.jpg', after_image_url='/static/images/portfolio/s5_a.jpg', description='Glass-skin celebrity reception style with Hollywood curls.')
        ]
        db.session.add_all(portfolios)
        db.session.commit()
        print("Salon portfolios seeded.")

        # 8. Add Wishlist and default Budget Plan for Priya
        wishlist_priya = Wishlist(user_id=bride.id)
        db.session.add(wishlist_priya)
        
        budget_priya = BudgetPlan(
            user_id=bride.id,
            total_budget=200000.0,
            dress_budget=80000.0,
            jewelry_budget=60000.0,
            makeup_budget=30000.0,
            accessories_budget=15000.0,
            emergency_budget=15000.0
        )
        db.session.add(budget_priya)
        db.session.commit()
        print("Priya's wishlist and budget initialized.")
        print("All sample data seeded successfully!")

if __name__ == '__main__':
    seed_db()

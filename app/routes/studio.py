from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, BridalLook, LookReview, UserPreference, BudgetPlan, Product, Category
from app.utils.ai_engine import get_hybrid_product_recommendations, get_recommended_salons, format_budget_plan

studio_bp = Blueprint('studio', __name__)

@studio_bp.route('/')
def gallery():
    looks = BridalLook.query.all()
    return render_template('studio/gallery.html', looks=looks)


@studio_bp.route('/look/<int:look_id>')
def look_detail(look_id):
    look = BridalLook.query.get_or_404(look_id)
    reviews = LookReview.query.filter_by(look_id=look_id).order_by(LookReview.created_at.desc()).all()
    
    # AI recommendations based on look
    pref = current_user.preference if current_user.is_authenticated else None
    recommended_products = get_hybrid_product_recommendations(user_pref=pref, look=look, limit=4)
    
    # Recommend top 3 salons (default coordinates: Vadodara)
    recommended_salons = get_recommended_salons(22.3072, 73.1812, look=look, limit=3)
    
    wishlisted = False
    if current_user.is_authenticated and current_user.wishlist:
        from app.models import WishlistItem
        item = WishlistItem.query.filter_by(wishlist_id=current_user.wishlist.id, look_id=look.id).first()
        wishlisted = item is not None

    return render_template('studio/look_detail.html', 
                           look=look, 
                           reviews=reviews, 
                           products=recommended_products, 
                           salons=recommended_salons,
                           wishlisted=wishlisted)


@studio_bp.route('/look/<int:look_id>/review', methods=['POST'])
@login_required
def add_look_review(look_id):
    rating = request.form.get('rating', 5)
    comment = request.form.get('comment', '')

    new_review = LookReview(
        user_id=current_user.id,
        look_id=look_id,
        rating=int(rating),
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()

    flash('Look review added successfully!', 'success')
    return redirect(url_for('studio.look_detail', look_id=look_id))


@studio_bp.route('/customizer', methods=['GET', 'POST'])
def customizer():
    if request.method == 'POST':
        skin_tone = request.form.get('skin_tone')
        face_shape = request.form.get('face_shape')
        hair_length = request.form.get('hair_length')
        wedding_theme = request.form.get('wedding_theme')
        jewelry_style = request.form.get('jewelry_style')
        budget_val = request.form.get('budget', 150000.0)
        pref_colors = request.form.get('preferred_colors', '')

        try:
            budget_val = float(budget_val)
        except ValueError:
            budget_val = 150000.0

        # Save preferences to logged-in user
        if current_user.is_authenticated and current_user.role == 'bride':
            pref = UserPreference.query.filter_by(user_id=current_user.id).first()
            if not pref:
                pref = UserPreference(
                    user_id=current_user.id,
                    skin_tone=skin_tone,
                    face_shape=face_shape,
                    hair_length=hair_length,
                    wedding_theme=wedding_theme,
                    preferred_colors=pref_colors,
                    jewelry_style=jewelry_style,
                    budget=budget_val
                )
                db.session.add(pref)
            else:
                pref.skin_tone = skin_tone
                pref.face_shape = face_shape
                pref.hair_length = hair_length
                pref.wedding_theme = wedding_theme
                pref.preferred_colors = pref_colors
                pref.jewelry_style = jewelry_style
                pref.budget = budget_val
            db.session.commit()

        # Run Recommendation Engine
        # Formulate a temporary preference object to run AI matches if user is guest
        class TempPref:
            def __init__(self):
                self.skin_tone = skin_tone
                self.face_shape = face_shape
                self.hair_length = hair_length
                self.wedding_theme = wedding_theme
                self.jewelry_style = jewelry_style
                self.budget = budget_val
                self.preferred_colors = pref_colors

        temp_pref = TempPref()
        recommended_products = get_hybrid_product_recommendations(user_pref=temp_pref, limit=6)
        
        # Match with default coordinates (Vadodara)
        recommended_salons = get_recommended_salons(22.3072, 73.1812, limit=3)

        # Highlight preset look that matches best
        matched_look = BridalLook.query.filter(BridalLook.theme_tags.like(f"%{skin_tone.lower()}%") | BridalLook.theme_tags.like(f"%{jewelry_style.lower()}%")).first()
        if not matched_look:
            matched_look = BridalLook.query.first()

        return render_template('studio/customizer_results.html', 
                               skin_tone=skin_tone,
                               face_shape=face_shape,
                               hair_length=hair_length,
                               wedding_theme=wedding_theme,
                               jewelry_style=jewelry_style,
                               budget=budget_val,
                               colors=pref_colors,
                               products=recommended_products,
                               salons=recommended_salons,
                               look=matched_look)

    return render_template('studio/customizer.html')


@studio_bp.route('/budget-planner', methods=['GET', 'POST'])
@login_required
def budget_planner():
    if current_user.role != 'bride':
        flash('Only brides can manage budget plans.', 'warning')
        return redirect(url_for('main.index'))

    plan = BudgetPlan.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        total = request.form.get('total_budget')
        try:
            total_budget = float(total)
        except (ValueError, TypeError):
            total_budget = 150000.0

        alloc = format_budget_plan(total_budget)
        if not plan:
            plan = BudgetPlan(
                user_id=current_user.id,
                total_budget=total_budget,
                dress_budget=alloc['dress'],
                jewelry_budget=alloc['jewelry'],
                makeup_budget=alloc['makeup'],
                accessories_budget=alloc['accessories'],
                emergency_budget=alloc['emergency']
            )
            db.session.add(plan)
        else:
            plan.total_budget = total_budget
            plan.dress_budget = alloc['dress']
            plan.jewelry_budget = alloc['jewelry']
            plan.makeup_budget = alloc['makeup']
            plan.accessories_budget = alloc['accessories']
            plan.emergency_budget = alloc['emergency']
        
        db.session.commit()
        flash('Budget allocations updated!', 'success')
        return redirect(url_for('studio.budget_planner'))

    # If plan exists, recommend catalog products matching budget ceilings!
    suggested_dresses = []
    suggested_jewelry = []
    suggested_accessories = []

    if plan:
        # Category maps (Dresses: Lehenga/Saree/Gown/Reception, Jewelry: Necklaces, Accessories: clutches, footwear)
        # Category ids: dresses=sub_lehenga (parent 1), jewelry (parent 2), accessories (parent 4)
        # We can query all products and match parent categories and check prices <= budget cap
        all_products = Product.query.all()
        for p in all_products:
            # Check parent category of product
            parent_cat_id = p.category.parent_id if p.category else None
            
            if parent_cat_id == 1 and p.price <= plan.dress_budget:  # Dresses
                suggested_dresses.append(p)
            elif parent_cat_id == 2 and p.price <= plan.jewelry_budget: # Jewelry
                suggested_jewelry.append(p)
            elif parent_cat_id == 4 and p.price <= plan.accessories_budget: # Accessories
                suggested_accessories.append(p)

    return render_template('studio/budget_planner.html', 
                           plan=plan,
                           dresses=suggested_dresses[:3],
                           jewelry=suggested_jewelry[:3],
                           accessories=suggested_accessories[:3])


@studio_bp.route('/try-on/<int:product_id>')
@login_required
def try_on(product_id):
    if current_user.role != 'bride':
        flash('Virtual Try-On is exclusive to brides.', 'warning')
        return redirect(url_for('shop.catalog'))
        
    product = Product.query.get_or_404(product_id)
    pref = current_user.preference
    return render_template('studio/try_on.html', product=product, pref=pref)

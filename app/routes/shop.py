from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, Product, Category, Wishlist, WishlistItem, Order, OrderItem, Review
from app.utils.ai_engine import get_hybrid_product_recommendations
from app.utils.notification_service import notify_order_status

shop_bp = Blueprint('shop', __name__)

@shop_bp.route('/')
def catalog():
    cat_id = request.args.get('category')
    sort_by = request.args.get('sort', 'new')
    search_query = request.args.get('q', '').strip()

    products_query = Product.query

    if cat_id:
        category = Category.query.get(int(cat_id))
        if category:
            cat_ids = [category.id] + [sub.id for sub in category.subcategories]
            products_query = products_query.filter(Product.category_id.in_(cat_ids))
    if search_query:
        products_query = products_query.filter(
            (Product.name.like(f"%{search_query}%")) |
            (Product.description.like(f"%{search_query}%")) |
            (Product.style_tags.like(f"%{search_query}%"))
        )

    # Sorting
    if sort_by == 'price_low':
        products_query = products_query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        products_query = products_query.order_by(Product.price.desc())
    else:
        products_query = products_query.order_by(Product.created_at.desc())

    products = products_query.all()
    categories = Category.query.all()

    # User's wishlist item ids to highlight filled hearts
    wishlisted_pids = []
    if current_user.is_authenticated and current_user.wishlist:
        wishlisted_pids = [item.product_id for item in current_user.wishlist.items if item.product_id]

    return render_template('shop/catalog.html', products=products, categories=categories, selected_cat=cat_id, sort=sort_by, q=search_query, wishlist_ids=wishlisted_pids)


@shop_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    
    # AI recommendations for related items
    pref = current_user.preference if current_user.is_authenticated else None
    recommendations = get_hybrid_product_recommendations(user_pref=pref, limit=4)
    # Exclude current product
    recommendations = [p for p in recommendations if p.id != product.id]

    wishlisted = False
    if current_user.is_authenticated and current_user.wishlist:
        item = WishlistItem.query.filter_by(wishlist_id=current_user.wishlist.id, product_id=product.id).first()
        wishlisted = item is not None

    return render_template('shop/detail.html', product=product, recommendations=recommendations, wishlisted=wishlisted)


@shop_bp.route('/product/<int:product_id>/review', methods=['POST'])
@login_required
def add_product_review(product_id):
    rating = request.form.get('rating', 5)
    comment = request.form.get('comment', '')

    new_review = Review(
        user_id=current_user.id,
        product_id=product_id,
        rating=int(rating),
        comment=comment
    )
    db.session.add(new_review)
    db.session.commit()

    flash('Product review added successfully!', 'success')
    return redirect(url_for('shop.product_detail', product_id=product_id))


@shop_bp.route('/wishlist/toggle', methods=['POST'])
@login_required
def toggle_wishlist():
    if current_user.role != 'bride':
        return jsonify({'success': False, 'message': 'Only brides can use wishlists.'}), 403

    data = request.get_json() or {}
    product_id = data.get('product_id')
    look_id = data.get('look_id')
    salon_id = data.get('salon_id')

    # Get user wishlist
    wishlist = current_user.wishlist
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id)
        db.session.add(wishlist)
        db.session.commit()

    # Find item
    item = None
    if product_id:
        item = WishlistItem.query.filter_by(wishlist_id=wishlist.id, product_id=product_id).first()
    elif look_id:
        item = WishlistItem.query.filter_by(wishlist_id=wishlist.id, look_id=look_id).first()
    elif salon_id:
        item = WishlistItem.query.filter_by(wishlist_id=wishlist.id, salon_id=salon_id).first()

    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed', 'message': 'Item removed from wishlist.'})
    else:
        new_item = WishlistItem(wishlist_id=wishlist.id, product_id=product_id, look_id=look_id, salon_id=salon_id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added', 'message': 'Item saved to wishlist.'})


@shop_bp.route('/cart', methods=['GET', 'POST'])
def cart_view():
    if 'cart' not in session:
        session['cart'] = {}
    
    # Process actions
    if request.method == 'POST':
        action = request.form.get('action')
        product_id = request.form.get('product_id')
        qty = request.form.get('quantity', 1)

        try:
            product_id = str(product_id)
            qty = int(qty)
        except (ValueError, TypeError):
            qty = 1

        cart = session['cart']

        if action == 'add':
            cart[product_id] = cart.get(product_id, 0) + qty
            flash('Item added to cart!', 'success')
        elif action == 'update':
            if qty <= 0:
                cart.pop(product_id, None)
            else:
                cart[product_id] = qty
            flash('Cart updated.', 'info')
        elif action == 'remove':
            cart.pop(product_id, None)
            flash('Item removed from cart.', 'info')

        session['cart'] = cart
        session.modified = True
        return redirect(url_for('shop.cart_view'))

    # Load details
    cart_items = []
    subtotal = 0.0
    for pid, qty in session['cart'].items():
        product = Product.query.get(int(pid))
        if product:
            item_total = product.price * qty
            subtotal += item_total
            cart_items.append({
                'product': product,
                'quantity': qty,
                'total': item_total
            })

    gst = subtotal * 0.18
    grand_total = subtotal + gst

    return render_template('shop/cart.html', items=cart_items, subtotal=subtotal, gst=gst, total=grand_total)


@shop_bp.route('/checkout')
@login_required
def checkout():
    if current_user.role != 'bride':
        flash('Only brides can perform orders.', 'warning')
        return redirect(url_for('shop.catalog'))

    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('shop.catalog'))

    subtotal = 0.0
    checkout_items = []
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal += product.price * qty
            checkout_items.append({'product': product, 'quantity': qty})

    gst = subtotal * 0.18
    grand_total = subtotal + gst

    return render_template('shop/checkout.html', items=checkout_items, subtotal=subtotal, gst=gst, total=grand_total)


@shop_bp.route('/payment/simulate', methods=['POST'])
@login_required
def simulate_payment():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'info')
        return redirect(url_for('shop.catalog'))

    shipping_address = request.form.get('shipping_address')
    phone = request.form.get('phone')
    payment_method = request.form.get('payment_method')  # 'Stripe' or 'Razorpay'
    simulate_status = request.form.get('simulate_status', 'success')  # 'success' or 'failure'

    if not shipping_address or not phone:
        flash('Please fill in shipping address and phone number.', 'danger')
        return redirect(url_for('shop.checkout'))

    subtotal = 0.0
    order_items_to_create = []
    for pid, qty in cart.items():
        product = Product.query.get(int(pid))
        if product:
            subtotal += product.price * qty
            order_items_to_create.append((product, qty))

    gst = subtotal * 0.18
    grand_total = subtotal + gst

    if simulate_status == 'failure':
        # Render mock payment failure message
        flash(f'Transaction failed via {payment_method}. Please try again.', 'danger')
        return redirect(url_for('shop.checkout'))

    # Success Flow:
    # 1. Create Order
    order = Order(
        user_id=current_user.id,
        status='Paid',
        total_amount=grand_total,
        gst_amount=gst,
        shipping_address=shipping_address,
        phone=phone,
        payment_method=payment_method,
        payment_status='Paid'
    )
    db.session.add(order)
    db.session.commit()

    # 2. Create OrderItems
    for prod, qty in order_items_to_create:
        item = OrderItem(
            order_id=order.id,
            product_id=prod.id,
            quantity=qty,
            price=prod.price
        )
        db.session.add(item)
    db.session.commit()

    # Trigger mock email/SMS
    notify_order_status(order)

    # Clear cart
    session.pop('cart', None)
    session.modified = True

    flash('Order placed and payment simulated successfully!', 'success')
    return render_template('shop/confirmation.html', order=order)


@shop_bp.route('/orders')
@login_required
def orders_list():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('shop/orders.html', orders=orders)

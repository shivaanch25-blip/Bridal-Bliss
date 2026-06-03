from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth_helpers import admin_required
from app.utils.audit import log_event
from app.models import db, Salon, Product, Category, BridalLook, User, Order

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Gather Global Analytics
    orders = Order.query.all()
    total_sales = sum([o.total_amount for o in orders if o.status == 'Paid'])
    order_count = len(orders)
    
    users = User.query.filter_by(role='bride').count()
    salon_owners = User.query.filter_by(role='salon_owner').count()

    # Salon Approvals List
    pending_salons = Salon.query.filter_by(is_approved=False).all()
    approved_salons = Salon.query.filter_by(is_approved=True).all()

    # Catalog
    products = Product.query.all()
    categories = Category.query.all()
    looks = BridalLook.query.all()

    return render_template('admin/dashboard.html',
                           sales=total_sales,
                           order_count=order_count,
                           brides=users,
                           owners=salon_owners,
                           pending_salons=pending_salons,
                           approved_salons=approved_salons,
                           products=products,
                           categories=categories,
                           looks=looks)


@admin_bp.route('/salon/<int:salon_id>/approve')
@admin_required
def approve_salon(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    salon.is_approved = True
    db.session.commit()
    log_event(current_user.id, 'update', 'salon', salon.id, f'Salon approved: {salon.name}')

    flash(f'Salon "{salon.name}" has been approved!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/salon/<int:salon_id>/delete')
@admin_required
def delete_salon(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    db.session.delete(salon)
    db.session.commit()
    log_event(current_user.id, 'delete', 'salon', salon.id, f'Salon deleted: {salon.name}')

    flash('Salon record deleted.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/product/add', methods=['POST'])
@admin_required
def add_product():
    name = request.form.get('name')
    desc = request.form.get('description')
    price = request.form.get('price', 0)
    cat_id = request.form.get('category_id')
    tier = request.form.get('budget_tier', 'midrange')
    tags = request.form.get('style_tags', '')
    img_url = request.form.get('image_url', '/static/images/products/default.jpg')

    try:
        price_val = float(price)
    except ValueError:
        price_val = 0.0

    new_prod = Product(
        name=name,
        description=desc,
        price=price_val,
        category_id=int(cat_id) if cat_id else 1,
        budget_tier=tier,
        style_tags=tags,
        image_url=img_url
    )
    db.session.add(new_prod)
    db.session.commit()
    log_event(current_user.id, 'create', 'product', new_prod.id, f'Product created: {new_prod.name}')

    flash('New product added to catalog.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/product/<int:product_id>/delete')
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    log_event(current_user.id, 'delete', 'product', product.id, f'Product deleted: {product.name}')

    flash('Product removed from catalog.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/look/add', methods=['POST'])
@admin_required
def add_look():

    name = request.form.get('name')
    makeup = request.form.get('makeup_style')
    hair = request.form.get('hairstyle')
    jewelry = request.form.get('jewelry_style')
    outfit = request.form.get('outfit_style')
    palette = request.form.get('color_palette')
    desc = request.form.get('description')
    tags = request.form.get('theme_tags')
    img_url = request.form.get('image_url', '/static/images/looks/default.jpg')

    new_look = BridalLook(
        name=name,
        makeup_style=makeup,
        hairstyle=hair,
        jewelry_style=jewelry,
        outfit_style=outfit,
        color_palette=palette,
        description=desc,
        theme_tags=tags,
        image_url=img_url
    )
    db.session.add(new_look)
    db.session.commit()
    log_event(current_user.id, 'create', 'bridal_look', new_look.id, f'Look created: {new_look.name}')

    flash('New AI Bridal Look created.', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/look/<int:look_id>/delete')
@admin_required
def delete_look(look_id):
    look = BridalLook.query.get_or_404(look_id)
    db.session.delete(look)
    db.session.commit()
    log_event(current_user.id, 'delete', 'bridal_look', look.id, f'Look deleted: {look.name}')

    flash('Bridal look deleted.', 'info')
    return redirect(url_for('admin.dashboard'))

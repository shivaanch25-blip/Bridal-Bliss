from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import (
    db,
    Salon,
    SalonService,
    Category,
    Product,
    BridalLook,
    Order,
    OrderItem,
    Appointment,
    Wishlist,
    WishlistItem,
    Notification,
)
from app.utils.errors import ValidationError

api_bp = Blueprint('api', __name__)


def api_response(data=None, message='Success', errors=None, status=200):
    payload = {
        'status': 'success' if status < 400 else 'error',
        'message': message,
        'data': data if data is not None else [] if status == 200 else None,
    }
    if errors is not None:
        payload['errors'] = errors
    return jsonify(payload), status


def validate_booking_payload(payload):
    required = ['salon_id', 'appointment_date', 'time_slot']
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValidationError(f'Missing required booking fields: {", ".join(missing)}')


def validate_order_payload(payload):
    required = ['shipping_address', 'phone', 'payment_method']
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValidationError(f'Missing required order fields: {", ".join(missing)}')

@api_bp.route('/salons/<int:salon_id>/services')
def get_salon_services(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    services_list = [
        {
            'id': s.id,
            'service_name': s.service_name,
            'price': s.price,
            'category': s.category,
        }
        for s in salon.services
    ]
    return jsonify({'salon_id': salon_id, 'salon_name': salon.name, 'services': services_list})


@api_bp.route('/products')
def list_products():
    query = Product.query
    category = request.args.get('category')
    q = request.args.get('q')

    if category:
        query = query.join(Product.category).filter(Category.name.ilike(f'%{category}%'))
    if q:
        query = query.filter(Product.name.ilike(f'%{q}%'))

    products = query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'category': product.category.name if product.category else None,
    } for product in products])


@api_bp.route('/products/<int:product_id>')
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'image_url': product.image_url,
        'category': product.category.name if product.category else None,
    })


@api_bp.route('/looks')
def list_looks():
    looks = BridalLook.query.all()
    return jsonify([{
        'id': look.id,
        'name': look.name,
        'description': look.description,
        'image_url': look.image_url,
        'theme_tags': look.theme_tags,
    } for look in looks])


@api_bp.route('/looks/<int:look_id>')
def get_look(look_id):
    look = BridalLook.query.get_or_404(look_id)
    return jsonify({
        'id': look.id,
        'name': look.name,
        'description': look.description,
        'image_url': look.image_url,
        'theme_tags': look.theme_tags,
    })


@api_bp.route('/bookings')
@login_required
def list_bookings():
    appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    return api_response([{
        'id': appointment.id,
        'salon_id': appointment.salon_id,
        'service': appointment.service,
        'appointment_date': appointment.appointment_date,
        'time_slot': appointment.time_slot,
        'status': appointment.status,
    } for appointment in appointments])


@api_bp.route('/bookings', methods=['POST'])
@login_required
def create_booking():
    payload = request.get_json() or {}
    validate_booking_payload(payload)

    salon_id = payload.get('salon_id')
    service = payload.get('service') or 'Bridal Styling'
    date = payload.get('appointment_date')
    time = payload.get('time_slot')
    notes = payload.get('notes', '')

    salon = Salon.query.get_or_404(salon_id)
    appointment = Appointment(
        user_id=current_user.id,
        salon_id=salon.id,
        service=service,
        appointment_date=date,
        time_slot=time,
        notes=notes,
        status='Pending',
    )
    db.session.add(appointment)
    db.session.commit()

    return api_response({'booking_id': appointment.id}, 'Booking created successfully.', status=201)


@api_bp.route('/orders')
@login_required
def list_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return api_response([{
        'id': order.id,
        'status': order.status,
        'total_amount': order.total_amount,
        'payment_status': order.payment_status,
        'created_at': order.created_at.isoformat(),
    } for order in orders])


@api_bp.route('/orders/<int:order_id>')
@login_required
def get_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    items = [{
        'product_id': item.product_id,
        'quantity': item.quantity,
        'price': item.price,
    } for item in order.items]
    return api_response({
        'id': order.id,
        'status': order.status,
        'total_amount': order.total_amount,
        'payment_status': order.payment_status,
        'items': items,
    })


@api_bp.route('/wishlist')
@login_required
def get_wishlist():
    wishlist = current_user.wishlist
    if not wishlist:
        return api_response([])
    return api_response([{
        'id': item.id,
        'product_id': item.product_id,
        'look_id': item.look_id,
        'salon_id': item.salon_id,
        'created_at': item.created_at.isoformat(),
    } for item in wishlist.items])


@api_bp.route('/wishlist/toggle', methods=['POST'])
@login_required
def toggle_wishlist_item():
    payload = request.get_json() or {}
    product_id = payload.get('product_id')
    look_id = payload.get('look_id')
    salon_id = payload.get('salon_id')

    if not any([product_id, look_id, salon_id]):
        raise ValidationError('Must provide product_id, look_id, or salon_id.')

    wishlist = current_user.wishlist
    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id)
        db.session.add(wishlist)
        db.session.commit()

    item = WishlistItem.query.filter_by(
        wishlist_id=wishlist.id,
        product_id=product_id,
        look_id=look_id,
        salon_id=salon_id,
    ).first()

    if item:
        db.session.delete(item)
        db.session.commit()
        return api_response(message='Wishlist item removed.')

    new_item = WishlistItem(
        wishlist_id=wishlist.id,
        product_id=product_id,
        look_id=look_id,
        salon_id=salon_id,
    )
    db.session.add(new_item)
    db.session.commit()
    return api_response({'item_id': new_item.id}, 'Wishlist item added.', status=201)


@api_bp.route('/openapi.json')
def openapi_doc():
    openapi = {
        'openapi': '3.0.0',
        'info': {
            'title': 'Bridal Bliss API',
            'version': '1.0.0',
            'description': 'Versioned API for Bridal Bliss enterprise workflows.'
        },
        'paths': {
            '/api/products': {
                'get': {
                    'summary': 'List products',
                    'responses': {'200': {'description': 'Product list response'}}
                }
            },
            '/api/looks': {
                'get': {
                    'summary': 'List bridal looks',
                    'responses': {'200': {'description': 'Look list response'}}
                }
            },
            '/api/bookings': {
                'get': {
                    'summary': 'List bookings for authenticated user',
                    'responses': {'200': {'description': 'Booking list response'}}
                },
                'post': {
                    'summary': 'Create booking for authenticated user',
                    'responses': {'201': {'description': 'Booking created'}}
                }
            }
        }
    }
    return jsonify(openapi)


@api_bp.route('/')
def api_root():
    return jsonify({
        'status': 'success',
        'message': 'Bridal Bliss API root. Use /api/docs or /api/openapi.json for API documentation.',
        'docs': '/api/docs',
        'openapi': '/api/openapi.json'
    })


@api_bp.route('/docs')
def docs():
    return jsonify({
        'message': 'API documentation is available at /api/openapi.json and /api/v1/openapi.json',
        'openapi': '/api/openapi.json'
    })

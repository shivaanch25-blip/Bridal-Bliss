from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth_helpers import owner_required
from app.utils.audit import log_event
from flask_login import current_user
from app.models import db, Salon, SalonService, SalonPortfolio, Appointment
from app.services.notification_service import NotificationService

owner_bp = Blueprint('owner', __name__)

@owner_bp.route('/dashboard')
@owner_required
def dashboard():

    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    
    if not salon:
        # User needs to register their salon
        return render_template('salon_owner/register_salon.html')

    # Gather metrics
    pending_bookings = Appointment.query.filter_by(salon_id=salon.id, status='Pending').all()
    confirmed_bookings = Appointment.query.filter_by(salon_id=salon.id, status='Confirmed').all()
    completed_bookings = Appointment.query.filter_by(salon_id=salon.id, status='Completed').all()
    
    revenue = sum([b.total_price for b in completed_bookings])

    return render_template('salon_owner/dashboard.html', 
                           salon=salon, 
                           pending=pending_bookings, 
                           confirmed=confirmed_bookings, 
                           completed=completed_bookings,
                           revenue=revenue)


@owner_bp.route('/register-salon', methods=['POST'])
@owner_required
def register_salon():

    name = request.form.get('name')
    description = request.form.get('description')
    contact = request.form.get('contact')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    pincode = request.form.get('pincode')
    lat = request.form.get('latitude', 22.3072)
    lon = request.form.get('longitude', 73.1812)

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        latitude, longitude = 22.3072, 73.1812

    new_salon = Salon(
        name=name,
        description=description,
        contact_number=contact,
        address=address,
        city=city,
        state=state,
        pincode=pincode,
        latitude=latitude,
        longitude=longitude,
        owner_id=current_user.id,
        is_approved=False  # Must be approved by administrator
    )
    db.session.add(new_salon)
    db.session.commit()
    log_event(current_user.id, 'create', 'salon', new_salon.id, f'Salon registered: {new_salon.name}')

    flash('Salon registered successfully! Waiting for administrator approval.', 'success')
    return redirect(url_for('owner.dashboard'))


@owner_bp.route('/appointment/<int:booking_id>/status/<string:action>')
@owner_required
def update_appointment_status(booking_id, action):
    booking = Appointment.query.get_or_404(booking_id)
    if booking.salon.owner_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('owner.dashboard'))

    if action == 'confirm':
        booking.status = 'Confirmed'
        flash('Appointment confirmed.', 'success')
    elif action == 'reject':
        booking.status = 'Cancelled'
        flash('Appointment cancelled.', 'info')
    elif action == 'complete':
        booking.status = 'Completed'
        flash('Appointment marked as Completed.', 'success')

    NotificationService.notify_booking_status(booking)
    db.session.commit()
    log_event(current_user.id, 'update', 'appointment', booking.id, f'Booking status updated to {booking.status}')
    return redirect(url_for('owner.dashboard'))


@owner_bp.route('/services/manage', methods=['GET', 'POST'])
@owner_required
def manage_services():

    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        return redirect(url_for('owner.dashboard'))

    if request.method == 'POST':
        name = request.form.get('service_name')
        price = request.form.get('price')
        category = request.form.get('category')  # 'makeup', 'hair', 'styling'

        try:
            price_val = float(price)
        except ValueError:
            price_val = 500.0

        new_service = SalonService(
            salon_id=salon.id,
            service_name=name,
            price=price_val,
            category=category
        )
        db.session.add(new_service)
        db.session.commit()
        log_event(current_user.id, 'create', 'salon_service', new_service.id, f'Service added: {new_service.service_name}')
        flash('Service added successfully.', 'success')
        return redirect(url_for('owner.manage_services'))

    services = SalonService.query.filter_by(salon_id=salon.id).all()
    return render_template('salon_owner/services.html', services=services, salon=salon)


@owner_bp.route('/services/<int:service_id>/delete')
@owner_required
def delete_service(service_id):
    service = SalonService.query.get_or_404(service_id)
    if service.salon.owner_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('owner.dashboard'))

    db.session.delete(service)
    db.session.commit()
    log_event(current_user.id, 'delete', 'salon_service', service.id, f'Service deleted: {service.service_name}')
    flash('Service deleted successfully.', 'info')
    return redirect(url_for('owner.manage_services'))


@owner_bp.route('/portfolio/manage', methods=['GET', 'POST'])
@owner_required
def manage_portfolio():

    salon = Salon.query.filter_by(owner_id=current_user.id).first()
    if not salon:
        return redirect(url_for('owner.dashboard'))

    if request.method == 'POST':
        desc = request.form.get('description')
        before_url = request.form.get('before_url', '/static/images/portfolio/default_before.jpg')
        after_url = request.form.get('after_url', '/static/images/portfolio/default_after.jpg')

        new_item = SalonPortfolio(
            salon_id=salon.id,
            before_image_url=before_url,
            after_image_url=after_url,
            description=desc
        )
        db.session.add(new_item)
        db.session.commit()
        log_event(current_user.id, 'create', 'salon_portfolio', new_item.id, 'Portfolio item added')
        flash('Transformation photo added to portfolio.', 'success')
        return redirect(url_for('owner.manage_portfolio'))

    portfolio_items = SalonPortfolio.query.filter_by(salon_id=salon.id).all()
    return render_template('salon_owner/portfolio.html', items=portfolio_items, salon=salon)


@owner_bp.route('/portfolio/<int:portfolio_id>/delete')
@owner_required
def delete_portfolio(portfolio_id):
    item = SalonPortfolio.query.get_or_404(portfolio_id)
    if item.salon.owner_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('owner.dashboard'))

    db.session.delete(item)
    db.session.commit()
    log_event(current_user.id, 'delete', 'salon_portfolio', item.id, 'Portfolio item deleted')
    flash('Portfolio item deleted.', 'info')
    return redirect(url_for('owner.manage_portfolio'))

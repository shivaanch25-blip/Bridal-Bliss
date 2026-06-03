from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Salon, SalonService, SalonPortfolio, Appointment, Review, BridalLook, ChatHistory
from app.utils.ai_engine import haversine_distance, BridalChatbot

main_bp = Blueprint('main', __name__)

# Mock geocoder mapping common Indian cities to coordinates for distance computations
CITY_COORDS = {
    'vadodara': (22.3072, 73.1812),
    'ahmedabad': (23.0225, 72.5714),
    'surat': (21.1702, 72.8311),
    'rajkot': (22.3039, 70.8022),
    'mumbai': (19.0760, 72.8777),
    'delhi': (28.6139, 77.2090),
    'bangalore': (12.9716, 77.5946),
    'hyderabad': (17.3850, 78.4867),
    'kolkata': (22.5726, 88.3639),
    'chennai': (13.0827, 80.2707)
}

PINCODE_COORDS = {
    '390007': (22.3112, 73.1754), # Alkapuri, Vadodara
    '380009': (23.0250, 72.5680), # CG Road, Ahmedabad
    '395007': (21.1512, 72.7932), # Vesu, Surat
    '360007': (22.2980, 70.7915), # Rajkot
    '400050': (19.0596, 72.8295), # Bandra, Mumbai
    '110001': (28.6304, 77.2177), # CP, Delhi
    '560038': (12.9784, 77.6408)  # Indiranagar, Bangalore
}

@main_bp.route('/')
def index():
    featured_looks = BridalLook.query.limit(3).all()
    # Find top rated salons
    top_salons = Salon.query.filter_by(is_approved=True).order_by(Salon.rating.desc()).limit(3).all()
    return render_template('index.html', looks=featured_looks, salons=top_salons)


@main_bp.route('/salons')
def salons_list():
    query_text = request.args.get('q', '').strip()
    city_filter = request.args.get('city', '').strip()
    pincode_filter = request.args.get('pincode', '').strip()
    service_type = request.args.get('service', '').strip()
    max_dist = request.args.get('distance', 50)
    
    try:
        max_dist = float(max_dist)
    except ValueError:
        max_dist = 50.0

    # User coordinate setup (default to Vadodara)
    user_lat, user_lon = 22.3072, 73.1812
    has_coords = False

    if pincode_filter in PINCODE_COORDS:
        user_lat, user_lon = PINCODE_COORDS[pincode_filter]
        has_coords = True
    elif city_filter.lower() in CITY_COORDS:
        user_lat, user_lon = CITY_COORDS[city_filter.lower()]
        has_coords = True

    # Base query for approved salons
    salons_query = Salon.query.filter_by(is_approved=True)

    if city_filter and not has_coords:
        salons_query = salons_query.filter(Salon.city.like(f"%{city_filter}%"))
    if pincode_filter and not has_coords:
        salons_query = salons_query.filter_by(pincode=pincode_filter)
    if query_text:
        salons_query = salons_query.filter(
            (Salon.name.like(f"%{query_text}%")) |
            (Salon.description.like(f"%{query_text}%"))
        )

    all_salons = salons_query.all()
    final_salons = []

    for s in all_salons:
        # Distance calculation
        distance = haversine_distance(user_lat, user_lon, s.latitude, s.longitude)
        
        # Filter by service capability
        service_match = True
        if service_type:
            services = [srv.category for srv in s.services]
            if service_type not in services:
                service_match = False
                
        # Filter by distance if user queried location
        if has_coords and distance > max_dist:
            continue

        if service_match:
            final_salons.append({
                'salon': s,
                'distance': distance
            })

    # Sort results
    # If location is provided, sort by distance. Otherwise by rating
    if has_coords:
        final_salons.sort(key=lambda x: x['distance'])
    else:
        final_salons.sort(key=lambda x: x['salon'].rating, reverse=True)

    return render_template('salons/list.html', salons=final_salons, has_coords=has_coords, query=query_text, city=city_filter, pincode=pincode_filter, distance=max_dist)


@main_bp.route('/salons/<int:salon_id>')
def salon_detail(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    # Available bridal looks to choose for booking
    looks = BridalLook.query.all()
    return render_template('salons/detail.html', salon=salon, looks=looks)


@main_bp.route('/salons/<int:salon_id>/review', methods=['POST'])
@login_required
def add_salon_review(salon_id):
    rating = request.form.get('rating', 5)
    comment = request.form.get('comment', '')
    
    new_review = Review(
        user_id=current_user.id,
        salon_id=salon_id,
        rating=int(rating),
        comment=comment
    )
    db.session.add(new_review)
    
    # Recalculate average rating
    salon = Salon.query.get_or_404(salon_id)
    reviews = Review.query.filter_by(salon_id=salon_id).all()
    total_rating = sum([r.rating for r in reviews]) + int(rating)
    salon.rating = round(total_rating / (len(reviews) + 1), 1)
    
    db.session.commit()
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('main.salon_detail', salon_id=salon_id))


@main_bp.route('/salons/<int:salon_id>/book', methods=['POST'])
@login_required
def book_appointment(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    look_id = request.form.get('look_id')
    date = request.form.get('date')
    slot = request.form.get('time_slot')
    home_service = request.form.get('home_service') == 'true'
    notes = request.form.get('notes')
    price_val = request.form.get('total_price')

    try:
        total_price = float(price_val)
    except (ValueError, TypeError):
        total_price = 10000.0  # Default fallback base

    new_booking = Appointment(
        user_id=current_user.id,
        salon_id=salon_id,
        look_id=int(look_id) if look_id else None,
        appointment_date=date,
        time_slot=slot,
        home_service=home_service,
        total_price=total_price,
        notes=notes,
        status='Pending'
    )
    db.session.add(new_booking)
    db.session.commit()
    
    flash('Appointment booked successfully! Awaiting owner confirmation.', 'success')
    return redirect(url_for('main.salon_detail', salon_id=salon_id))


@main_bp.route('/chatbot', methods=['POST'])
def chatbot_chat():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': 'How can I assist you in your bridal preparations today?'})
        
    bot = BridalChatbot(user=current_user if current_user.is_authenticated else None)
    response = bot.respond(message)

    # Save to history if logged in
    if current_user.is_authenticated:
        chat_user = ChatHistory(user_id=current_user.id, sender='user', message=message)
        chat_bot = ChatHistory(user_id=current_user.id, sender='bot', message=response)
        db.session.add_all([chat_user, chat_bot])
        db.session.commit()

    return jsonify({'response': response})

from flask import Blueprint, jsonify
from app.models import Salon, SalonService

api_bp = Blueprint('api', __name__)

@api_bp.route('/salons/<int:salon_id>/services')
def get_salon_services(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    services_list = []
    for s in salon.services:
        services_list.append({
            'id': s.id,
            'service_name': s.service_name,
            'price': s.price,
            'category': s.category
        })
    return jsonify({
        'salon_id': salon_id,
        'salon_name': salon.name,
        'services': services_list
    })

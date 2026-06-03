import json
import sys
import re
from app import create_app
from app.models import db, User, Category, Product, BridalLook, Salon, SalonService, Wishlist


def seed_minimal(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        admin = User(username='admin', email='admin@bridalbliss.com', role='admin')
        admin.set_password('admin123')
        bride = User(username='priya', email='priya@gmail.com', role='bride')
        bride.set_password('priya123')
        owner = User(username='owner1', email='owner1@bridalbliss.com', role='salon_owner')
        owner.set_password('owner123')
        db.session.add_all([admin, bride, owner])
        db.session.commit()

        wishlist = Wishlist(user_id=bride.id)
        db.session.add(wishlist)

        cat = Category(name='Lehenga')
        db.session.add(cat)
        db.session.commit()

        product = Product(name='Audit Lehenga', description='Audit product', price=1000.0, category_id=cat.id)
        db.session.add(product)

        look = BridalLook(name='Audit Look', makeup_style='Simple', image_url='')
        db.session.add(look)

        salon = Salon(name='Audit Salon', description='Test', contact_number='9999999999', address='Addr', city='City', state='S', pincode='000000', latitude=0.0, longitude=0.0, owner_id=owner.id, is_approved=True)
        db.session.add(salon)
        db.session.commit()

        service = SalonService(salon_id=salon.id, service_name='Makeup', price=500, category='makeup')
        db.session.add(service)
        db.session.commit()


def resolve_route_with_dummy_values(route):
    defaults = {
        'int': '1',
        'float': '1.0',
        'string': 'test',
        'path': 'test',
        'uuid': '00000000-0000-0000-0000-000000000000',
    }
    def replace_placeholder(match):
        type_name = match.group(1) or 'string'
        return defaults.get(type_name, 'test')

    return re.sub(r'<(?:(\w+):)?[^>]+>', replace_placeholder, route)


def crawl_routes(app):
    results = []
    with app.test_client() as client:
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
            # skip static
            if rule.endpoint.startswith('static'):
                continue
            methods = rule.methods
            if 'GET' not in methods:
                results.append({'rule': rule.rule, 'methods': list(methods), 'skipped': True, 'reason': 'no GET'})
                continue
            url = resolve_route_with_dummy_values(rule.rule)
            try:
                resp = client.get(url, follow_redirects=True)
                results.append({'rule': rule.rule, 'url': url, 'status_code': resp.status_code, 'endpoint': rule.endpoint})
            except Exception as e:
                results.append({'rule': rule.rule, 'url': url, 'error': str(e), 'endpoint': rule.endpoint})
    return results


def main():
    cfg = 'config.TestingConfig'
    app = create_app(cfg)
    seed_minimal(app)

    with app.app_context():
        total_routes = len([r for r in app.url_map.iter_rules() if not r.endpoint.startswith('static')])
    results = crawl_routes(app)

    summary = {
        'total_routes': total_routes,
        'checked': len(results),
        'results': results,
    }
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

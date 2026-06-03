import pytest
from app import create_app
from app.models import db, User, Category, Product, BridalLook, Salon, SalonService, Wishlist, Notification

@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    with app.app_context():
        db.drop_all()
        db.create_all()

        bride = User(username='priya', email='priya@gmail.com', role='bride')
        bride.set_password('priya123')
        db.session.add(bride)

        owner = User(username='owner1', email='owner1@bridalbliss.com', role='salon_owner')
        owner.set_password('owner123')
        db.session.add(owner)

        db.session.commit()

        wishlist = Wishlist(user_id=bride.id)
        db.session.add(wishlist)

        category = Category(name='Lehenga')
        db.session.add(category)
        db.session.commit()

        product = Product(
            name='Test Lehenga',
            description='A test bridal lehenga product.',
            price=115000.0,
            category_id=category.id,
            image_url='https://example.com/image.jpg',
            budget_tier='luxury',
            style_tags='traditional, red, gold'
        )
        db.session.add(product)

        look = BridalLook(
            name='Test Look',
            makeup_style='Soft glam',
            hairstyle='Low bun',
            jewelry_style='Kundan',
            outfit_style='Lehenga',
            color_palette='Red, Gold',
            description='A test look for the bridal studio.',
            image_url='https://example.com/look.jpg',
            theme_tags='traditional, red, gold'
        )
        db.session.add(look)

        salon = Salon(
            name='Test Salon',
            description='A test bridal salon.',
            contact_number='9999999999',
            address='123 Bridal Lane',
            city='Vadodara',
            state='Gujarat',
            pincode='390001',
            rating=4.5,
            experience_years=8,
            latitude=22.3072,
            longitude=73.1812,
            is_approved=True,
            owner_id=owner.id
        )
        db.session.add(salon)
        db.session.commit()

        salon_service = SalonService(
            salon_id=salon.id,
            service_name='Bridal Makeup',
            price=8000.0,
            category='makeup'
        )
        db.session.add(salon_service)

        notification = Notification(
            user_id=bride.id,
            message='Welcome to Bridal Bliss! Your account was created successfully.',
            is_read=False
        )
        db.session.add(notification)

        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

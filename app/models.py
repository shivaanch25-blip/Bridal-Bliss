from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='bride', nullable=False)  # 'bride', 'salon_owner', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    preference = db.relationship('UserPreference', back_populates='user', uselist=False, cascade="all, delete-orphan")
    budget_plan = db.relationship('BudgetPlan', back_populates='user', uselist=False, cascade="all, delete-orphan")
    wishlist = db.relationship('Wishlist', back_populates='user', uselist=False, cascade="all, delete-orphan")
    appointments = db.relationship('Appointment', back_populates='user', cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='user', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='user', cascade="all, delete-orphan")
    look_reviews = db.relationship('LookReview', back_populates='user', cascade="all, delete-orphan")
    chat_histories = db.relationship('ChatHistory', back_populates='user', cascade="all, delete-orphan")
    owned_salons = db.relationship('Salon', back_populates='owner', cascade="all, delete-orphan")
    notifications = db.relationship('Notification', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    products = db.relationship('Product', back_populates='category', cascade="all, delete-orphan")


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(256))
    budget_tier = db.Column(db.String(20), default='midrange', nullable=False) # 'budget', 'midrange', 'luxury'
    style_tags = db.Column(db.String(256))  # Comma-separated list: e.g., 'traditional, gold, heavy'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    category = db.relationship('Category', back_populates='products')
    reviews = db.relationship('Review', back_populates='product', cascade="all, delete-orphan")
    order_items = db.relationship('OrderItem', back_populates='product')
    wishlist_items = db.relationship('WishlistItem', back_populates='product', cascade="all, delete-orphan")


class BridalLook(db.Model):
    __tablename__ = 'bridal_looks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    makeup_style = db.Column(db.String(128))
    hairstyle = db.Column(db.String(128))
    jewelry_style = db.Column(db.String(128))
    outfit_style = db.Column(db.String(128))
    color_palette = db.Column(db.String(128))  # Comma-separated list: e.g., 'crimson, gold, ivory'
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    theme_tags = db.Column(db.String(256))  # e.g., 'gujarati, traditional, heavy'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    look_reviews = db.relationship('LookReview', back_populates='look', cascade="all, delete-orphan")
    appointments = db.relationship('Appointment', back_populates='look')
    wishlist_items = db.relationship('WishlistItem', back_populates='look', cascade="all, delete-orphan")


class LookReview(db.Model):
    __tablename__ = 'look_reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    look_id = db.Column(db.Integer, db.ForeignKey('bridal_looks.id'), nullable=False)
    rating = db.Column(db.Integer, default=5, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='look_reviews')
    look = db.relationship('BridalLook', back_populates='look_reviews')


class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    skin_tone = db.Column(db.String(64))  # e.g. 'Fair', 'Medium', 'Dusk', 'Deep'
    face_shape = db.Column(db.String(64))  # e.g. 'Oval', 'Round', 'Heart', 'Square'
    hair_length = db.Column(db.String(64))  # e.g. 'Short', 'Medium', 'Long'
    wedding_theme = db.Column(db.String(128))  # e.g. 'Traditional Gujarati', 'Royal Rajput', 'Modern Luxury'
    budget = db.Column(db.Float)
    preferred_colors = db.Column(db.String(256))  # Comma-separated list: e.g. 'Red, Gold'
    jewelry_style = db.Column(db.String(128))  # e.g. 'Kundan', 'Temple', 'Diamond', 'Antique Gold'
    face_image_path = db.Column(db.String(256))  # Path to uploaded photo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='preference')


class Salon(db.Model):
    __tablename__ = 'salons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    contact_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    rating = db.Column(db.Float, default=4.0)
    experience_years = db.Column(db.Integer, default=5)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    owner = db.relationship('User', back_populates='owned_salons')
    services = db.relationship('SalonService', back_populates='salon', cascade="all, delete-orphan")
    portfolio = db.relationship('SalonPortfolio', back_populates='salon', cascade="all, delete-orphan")
    appointments = db.relationship('Appointment', back_populates='salon', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='salon', cascade="all, delete-orphan")
    wishlist_items = db.relationship('WishlistItem', back_populates='salon', cascade="all, delete-orphan")


class SalonPortfolio(db.Model):
    __tablename__ = 'salon_portfolios'
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    before_image_url = db.Column(db.String(256))
    after_image_url = db.Column(db.String(256))
    description = db.Column(db.Text)

    # Relationships
    salon = db.relationship('Salon', back_populates='portfolio')


class SalonService(db.Model):
    __tablename__ = 'salon_services'
    id = db.Column(db.Integer, primary_key=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    service_name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)  # 'makeup', 'hair', 'styling'

    # Relationships
    salon = db.relationship('Salon', back_populates='services')


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=False)
    look_id = db.Column(db.Integer, db.ForeignKey('bridal_looks.id'), nullable=True)
    appointment_date = db.Column(db.String(64), nullable=False)  # YYYY-MM-DD
    time_slot = db.Column(db.String(64), nullable=False)  # e.g., '10:00 AM - 12:00 PM'
    status = db.Column(db.String(32), default='Pending')  # 'Pending', 'Confirmed', 'Completed', 'Cancelled'
    home_service = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='appointments')
    salon = db.relationship('Salon', back_populates='appointments')
    look = db.relationship('BridalLook', back_populates='appointments')


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # Relationships
    user = db.relationship('User', back_populates='wishlist')
    items = db.relationship('WishlistItem', back_populates='wishlist', cascade="all, delete-orphan")


class WishlistItem(db.Model):
    __tablename__ = 'wishlist_items'
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('wishlists.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    look_id = db.Column(db.Integer, db.ForeignKey('bridal_looks.id'), nullable=True)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=True)

    # Relationships
    wishlist = db.relationship('Wishlist', back_populates='items')
    product = db.relationship('Product', back_populates='wishlist_items')
    look = db.relationship('BridalLook', back_populates='wishlist_items')
    salon = db.relationship('Salon', back_populates='wishlist_items')


class BudgetPlan(db.Model):
    __tablename__ = 'budget_plans'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    total_budget = db.Column(db.Float, nullable=False)
    dress_budget = db.Column(db.Float, default=0.0)
    jewelry_budget = db.Column(db.Float, default=0.0)
    makeup_budget = db.Column(db.Float, default=0.0)
    accessories_budget = db.Column(db.Float, default=0.0)
    emergency_budget = db.Column(db.Float, default=0.0)

    # Relationships
    user = db.relationship('User', back_populates='budget_plan')


class ChatHistory(db.Model):
    __tablename__ = 'chat_histories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender = db.Column(db.String(10), nullable=False)  # 'user', 'bot'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='chat_histories')


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(32), default='Pending')  # 'Pending', 'Paid', 'Shipped', 'Delivered', 'Cancelled'
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, nullable=False)
    shipping_address = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(64))  # 'Stripe', 'Razorpay'
    payment_status = db.Column(db.String(32), default='Unpaid')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Float, nullable=False)

    # Relationships
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='order_items')


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    salon_id = db.Column(db.Integer, db.ForeignKey('salons.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    rating = db.Column(db.Integer, default=5, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='reviews')
    salon = db.relationship('Salon', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='notifications')


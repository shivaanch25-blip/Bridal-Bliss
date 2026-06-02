import os
from flask import Flask, session
from flask_login import LoginManager
from app.models import db, User, Wishlist

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Custom Jinja filters
    @app.template_filter('currency')
    def currency_filter(value):
        try:
            return f"₹{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"₹{value}"

    # Global context processors for templates
    @app.context_processor
    def inject_global_vars():
        # Cart size
        cart = session.get('cart', {})
        cart_count = sum(cart.values())
        return dict(cart_count=cart_count)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.shop import shop_bp
    from app.routes.studio import studio_bp
    from app.routes.salon_owner import owner_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp, url_prefix='/shop')
    app.register_blueprint(studio_bp, url_prefix='/studio')
    app.register_blueprint(owner_bp, url_prefix='/owner')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

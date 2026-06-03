import json
import logging
import os
from flask import Flask, session, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from werkzeug.exceptions import HTTPException
from app.models import db, User, Wishlist
from app.utils.errors import AppError

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

    # Structured logging for runtime events
    if not app.logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
        )
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)

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

        # Notification badge count for authenticated users
        notification_count = 0
        if current_user.is_authenticated:
            notification_count = sum(1 for n in current_user.notifications if not n.is_read)

        return dict(cart_count=cart_count, notification_count=notification_count)

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

    # API version compatibility alias
    @app.route('/api/v1')
    @app.route('/api/v1/<path:subpath>')
    def api_v1_compat(subpath=None):
        target = '/api'
        if subpath:
            target = f'/api/{subpath}'
        return redirect(target)

    # Central exception handling
    @app.errorhandler(AppError)
    def handle_app_error(error):
        app.logger.warning(json.dumps({
            'type': 'app_error',
            'message': error.message,
            'status_code': error.status_code,
            'payload': error.payload
        }))
        return render_template('errors/error.html', error=error), error.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        app.logger.warning(json.dumps({
            'type': 'http_exception',
            'code': error.code,
            'name': error.name,
            'description': error.description
        }))
        if error.code == 404:
            return render_template('errors/404.html', error=error), 404
        if error.code == 403:
            return render_template('errors/403.html', error=error), 403
        return render_template('errors/error.html', error=error), error.code

    @app.errorhandler(Exception)
    def handle_uncaught_exception(error):
        app.logger.exception('Unhandled exception occurred')
        return render_template('errors/500.html', error=error), 500

    return app

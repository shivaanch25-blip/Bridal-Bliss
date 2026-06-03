# System Architecture

## Application Architecture

Bridal Bliss is built as a Flask application using the application factory pattern. The app is configured through `config.py` and initializes extensions in `app/__init__.py`.

Key architecture components:

- Flask application factory (`app.create_app`)
- Blueprints for modular route and feature separation
- SQLAlchemy models in `app/models.py`
- Template-based UI rendering with Jinja2
- JSON API endpoints under `app/routes/api.py`
- Utility services in `app/utils`

## Blueprint Structure

The app is organized into blueprints by feature:

- `app/routes/auth.py`
  - Login, logout, registration, profile, notifications
- `app/routes/main.py`
  - Home page, salons listing, salon detail
- `app/routes/shop.py`
  - Product catalog, cart, checkout, orders
- `app/routes/studio.py`
  - Bridal looks, customizer, gallery, budget planner
- `app/routes/salon_owner.py`
  - Salon owner dashboard, salon registration, service management, portfolio
- `app/routes/admin.py`
  - Admin dashboard, approvals, product and salon management
- `app/routes/api.py`
  - REST API endpoints with standardized JSON responses

## Service Layer Architecture

Supporting services are implemented in `app/utils`:

- `app/utils/ai_engine.py`
  - Hybrid product recommendations
  - Salon ranking by distance, rating, and service capability
  - Budget planning and chatbot-style responses
- `app/utils/notification_service.py`
  - Notification creation and user delivery
- `app/utils/audit.py`
  - Audit logging for important user actions and system events

## Request Flow

1. Client issues a request to a route.
2. Flask routes are resolved through blueprints.
3. Route handlers perform authentication, authorization, and business logic.
4. The handler interacts with SQLAlchemy models and the database.
5. Responses are rendered via templates or returned as JSON.
6. Errors are handled centrally in `app/__init__.py`.

### Example request flow

- User opens `/shop/`
- `shop.catalog` loads products from `Product` model
- Data is passed to `templates/shop/catalog.html`
- Final HTML response renders the catalog page

## Database Relationships

The database is modeled in `app/models.py` with 19 tables.

Primary entities:

- `User`
  - Roles: `bride`, `salon_owner`, `admin`
  - Has preferences, budget plan, wishlist, appointments, orders, reviews, and notifications
- `Category` → `Product`
  - Product categories and subcategories support hierarchical catalog browsing
- `Product`
  - Products can have reviews, order items, and wishlist items
- `BridalLook`
  - Bridal looks can have reviews, appointments, and wishlist entries
- `Salon`
  - Owned by a `User`; contains services, portfolio entries, appointments, reviews, and wishlist references
- `Appointment`
  - Connects `User`, `Salon`, and optionally `BridalLook`
- `Wishlist` / `WishlistItem`
  - Supports products, looks, and salon recommendations
- `Order` / `OrderItem`
  - Tracks purchase orders and ordered products
- `AuditLog`
  - Stores key user and system activity for traceability

The architecture is intentionally normalized to support role-specific experiences, user personalization, and recommendation workflows.

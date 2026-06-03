# Bridal Bliss

Bridal Bliss is a production-ready bridal marketplace built with Flask, designed to connect brides, salon owners, and administrators through a complete wedding styling ecosystem.

## What it Does

- Enables brides to explore bridal looks, browse a product catalog, build wishlists, and simulate checkout.
- Supports salon owners to register salons, manage services, update bookings, and publish portfolio transformations.
- Provides admins with salon moderation, catalog management, and analytics dashboards.
- Includes AI-driven recommendation helpers for personalized product and salon suggestions.

## Key Features

- Role-based authentication and user management
- Bridal look gallery and customizable styling room
- Product catalog, wishlist, cart, and checkout flow
- Salon discovery, appointment booking, and status tracking
- Salon owner dashboard with portfolio and service management
- Admin portal for approvals and content moderation
- REST API for products, looks, bookings, orders, and wishlist data
- Centralized error handling and audit log tracking

## Tech Stack

- Python 3
- Flask 3
- Flask-SQLAlchemy
- Flask-Login
- Jinja2 templates
- SQLite (configurable via `DATABASE_URL`)
- Gunicorn for production serving
- Pytest for automated testing

## Architecture Overview

- App factory pattern in `app/__init__.py`
- Modular blueprints in `app/routes`
- Domain models in `app/models.py`
- AI helpers in `app/utils/ai_engine.py`
- Notification and audit services in `app/services`
- API routes in `app/routes/api.py`

## User Roles

- `bride` — personal bridal experience, wishlist, booking, and orders
- `salon_owner` — salon registration, services, bookings, portfolio
- `admin` — platform moderation, approvals, content management

## Install and Run

```bash
git clone https://github.com/shivaanch25-blip/Bridal-Bliss.git
cd Bridal-Bliss
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
python run.py
```

Open the app at `http://localhost:5000`.

## Environment Variables

Required environment variables:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///bridal_bliss.db
FLASK_ENV=development
PORT=5000
```

## Production Deployment

Run locally in production mode:

```bash
gunicorn run:app --log-file -
```

### Render Deployment

- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn run:app --log-file -`
- Configure `SECRET_KEY`, `DATABASE_URL`, `FLASK_ENV=production`, and `PORT`

## Testing

Execute the automated test suite:

```bash
python -m pytest -q
```

## Documentation and Portfolio Assets

- `deployment.md` — deployment checklist and Render instructions
- `docs/system_architecture.md` — system architecture overview
- `docs/api_reference.md` — API documentation
- `docs/database_schema.md` — database design and relationships
- `docs/deployment_guide.md` — deployment-ready instructions
- `docs/testing_guide.md` — test and validation guidance
- `PROJECT_SHOWCASE.md` — portfolio presentation summary
- `RESUME_PROJECT_SUMMARY.md` — concise resume-ready summary
- `FINAL_DEPLOYMENT_REPORT.md` — final audit and deployment report

## Recommended Demo Flows

- Browse the bridal look gallery and explore AI recommendations
- Add products to wishlist and complete a cart checkout simulation
- Register a salon and manage booking approvals as a salon owner
- Approve salons and add product catalog entries as an admin

## Notes

- The repo is ready for GitHub portfolio presentation and production deployment.
- Use `.env.example` to configure required environment variables.
- Seed sample data with `python seed.py` before first use.

# Deployment Guide

This guide covers local development setup and production-ready deployment for Bridal Bliss.

## Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/shivaanch25-blip/Bridal-Bliss.git
   cd Bridal-Bliss
   ```

2. Create a Python virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Or on Command Prompt:

   ```cmd
   .\.venv\Scripts\activate.bat
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Required Environment Variables

Create a `.env` file or configure the following in your host environment:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///bridal_bliss.db
FLASK_ENV=development
PORT=5000
```

### Recommended production values

- `SECRET_KEY`: strong random secret value
- `DATABASE_URL`: production database connection string (PostgreSQL / managed database)
- `FLASK_ENV=production`
- `PORT`: host assigned port or `10000`

## Database Initialization

Initialize the database and seed sample data:

```bash
python seed.py
```

This script recreates the schema and inserts sample users, categories, products, bridal looks, salons, and services.

## Run Locally

Start the app in development mode:

```bash
python run.py
```

Open your browser at:

```text
http://localhost:5000
```

## Production-style Startup

Use Gunicorn for a production-like environment:

```bash
gunicorn run:app --log-file -
```

## Render Deployment

Bridal Bliss is build-ready for Render.

1. Create a new Render Web Service.
2. Connect the GitHub repository.
3. Configure build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure start command:
   ```bash
   gunicorn run:app --log-file -
   ```
5. Add environment variables on the Render dashboard:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `FLASK_ENV=production`
   - `PORT`

## Production Readiness Checklist

- [x] `Procfile` exists with `gunicorn run:app --log-file -`
- [x] `config.py` supports `DATABASE_URL` and production config
- [x] `.env.example` documents required variables
- [x] No hardcoded secrets in code
- [x] `seed.py` present for data initialization
- [x] Error handling templates exist for 403, 404, 500, and generic errors

## Verification

After deployment, verify:

- Home page loads successfully
- Admin and salon owner dashboards are accessible by the correct user roles
- API endpoints such as `/api/products` return JSON
- 404 page renders for invalid paths
- Application logs do not contain unhandled exceptions

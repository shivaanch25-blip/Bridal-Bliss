# Bridal Bliss Deployment Guide

## Local Setup Instructions

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

## Dependency Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file or set the following environment variables in your shell or hosting platform:

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///bridal_bliss.db
FLASK_ENV=development
PORT=5000
```

### Recommended production values

- `SECRET_KEY`: strong random string
- `DATABASE_URL`: production database URI (Postgres or managed database)
- `FLASK_ENV`: `production`
- `PORT`: `10000` or use platform-assigned port

## Database Initialization

Initialize the database before launching the app:

```bash
python seed.py
```

This script recreates the database schema and inserts sample core users, categories, products, bridal looks, salons, and services.

## Running the Application

Start the app locally in development mode:

```bash
python run.py
```

Then open:

```text
http://localhost:5000
```

### Production-style startup

Use Gunicorn for production-style hosting:

```bash
gunicorn run:app --log-file -
```

## Running Tests

Run the project test suite with:

```bash
python -m pytest -q
```

## Render Deployment Instructions

The application is compatible with Render without code changes.

1. Create a new Web Service on Render.
2. Connect the GitHub repository.
3. Set the build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Set the start command:
   ```bash
   gunicorn run:app --log-file -
   ```
5. Add environment variables on Render:
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `FLASK_ENV=production`
   - `PORT` (Render usually provides this automatically)
6. If using Render Postgres, set `DATABASE_URL` to the Render Postgres URI.

### Notes for Render

- `run.py` reads `PORT` and the bootstrap settings from `DATABASE_URL`.
- `Procfile` is already included and compatible with Render's startup conventions.

## Notes

- If you want to keep the local SQLite database, you can continue using `DATABASE_URL=sqlite:///bridal_bliss.db`.
- For production, use a managed PostgreSQL database on Render or another provider.

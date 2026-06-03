# Testing Guide

This guide explains how to validate Bridal Bliss through automated tests and manual verification.

## Automated Test Setup

1. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the Test Suite

Run all tests with Pytest:

```bash
python -m pytest -q
```

Expected results:

- Product and look API endpoints should return JSON with status 200.
- Authentication and notification flows should succeed.
- Shopping cart and order simulation should complete successfully.

## Seeded Test Data

The test suite uses a minimal database seeded inside `tests/conftest.py`.

Seeded objects include:

- Bride user: `priya`
- Salon owner user: `owner1`
- Sample product
- Sample bridal look
- Sample approved salon
- Sample notification

## Manual Smoke Tests

Validate the following core user flows:

1. Home page loads: `http://localhost:5000`
2. User registration and login
3. Browse products, add to wishlist, and view cart
4. Simulate checkout and order creation
5. Browse bridal looks, add reviews, and use the studio customizer
6. Salon owner dashboard, salon registration, and service management
7. Admin dashboard, salon approval, product creation, and look creation
8. API endpoints under `/api`

## Route Audit Script

A route crawler is available at `scripts/audit_readiness.py`.

Run it with:

```bash
python scripts/audit_readiness.py
```

It validates all GET-accessible routes in the app and reports any failure responses.

## Test Coverage Notes

- The current automated suite covers authentication, core UI flows, API responses, and checkout workflow.
- Additional tests can be added for bridge owner management, wishlist toggling, and chat interaction.

## Failure Investigation

If tests fail:

1. Confirm environment variables are set correctly.
2. Re-run `python seed.py` to refresh the database.
3. Inspect the failing test output and traceback.
4. Use the app in the browser to reproduce the failed endpoint or flow.

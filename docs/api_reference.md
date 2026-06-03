# API Reference

## Overview

The Bridal Bliss API delivers product, bridal look, booking, wishlist, and order data through JSON endpoints.

Base API path: `/api`

### API Documentation

- `/api/` — API root status and documentation links
- `/api/docs` — API documentation page
- `/api/openapi.json` — OpenAPI JSON schema

## Authentication Endpoints

Authentication in Bridal Bliss uses website routes rather than a separate tokenized API.

- `POST /login`
  - Login with `username` and `password`
- `GET /logout`
  - Sign out current user
- `GET /register`
  - Registration page
- `POST /register`
  - Create a new user account
- `GET /notifications`
  - View authenticated user notifications
- `GET /profile`
  - View and edit the authenticated user profile

## Product Endpoints

- `GET /api/products`
  - List all products
- `GET /api/products/<int:product_id>`
  - Retrieve details for a single product

## Bridal Look Endpoints

- `GET /api/looks`
  - List bridal looks
- `GET /api/looks/<int:look_id>`
  - Get detailed bridal look information

## Booking Endpoints

- `GET /api/bookings`
  - Retrieve authenticated user bookings
- `POST /api/bookings`
  - Create a booking request

## Wishlist Endpoints

- `GET /api/wishlist`
  - Retrieve the current user wishlist
- `POST /api/wishlist/toggle`
  - Toggle a wishlist item on or off

## Order Endpoints

- `GET /api/orders`
  - List authenticated user orders
- `GET /api/orders/<int:order_id>`
  - View a single order

## Salon Endpoints

- `GET /api/salons/<int:salon_id>/services`
  - List services for a specific salon

## Notes

- Routes returning JSON use a standard payload wrapper for status, message, and data.
- Only GET endpoints are documented here for read operations; POST endpoints exist for creations and toggles.

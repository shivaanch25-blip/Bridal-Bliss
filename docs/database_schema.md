# Database Schema

Bridal Bliss uses a normalized relational schema implemented with SQLAlchemy and Flask-SQLAlchemy.

## Core Entities

- `User`
  - Stores login credentials, role, and basic profile data.
  - Roles: `bride`, `salon_owner`, `admin`.
  - Relationships: preference, budget plan, wishlist, appointments, orders, reviews, look reviews, notifications, owned salons.

- `Category`
  - Hierarchical product categories using self-referential parent/child relationships.
  - Supports top-level categories and subcategories like Lehenga, Jewelry, Makeup, and Accessories.
  - Relationship: products.

- `Product`
  - Catalog items sold through the shop.
  - Attributes: price, budget tier, image, style tags, created timestamp.
  - Relationships: category, reviews, order items, wishlist items.

- `BridalLook`
  - Curated bridal fashion looks used by the studio and recommendation engine.
  - Attributes: makeup style, hairstyle, jewelry style, outfit style, palette, theme tags.
  - Relationships: look reviews, appointments, wishlist items.

- `Salon`
  - Salon profiles created by salon owners.
  - Attributes: location, rating, approval status, contact details, owner reference.
  - Relationships: owner, services, portfolio, appointments, reviews, wishlist items.

- `SalonService`
  - Service offerings for each salon.
  - Attributes: service name, price, category.

- `SalonPortfolio`
  - Before/after showcase images for salon owners.
  - Attributes: description and image URLs.

- `Appointment`
  - Salon booking records.
  - Links brides to salons and optional bridal looks.
  - Tracks date, time slot, status, price, notes.

- `Wishlist` / `WishlistItem`
  - A single wishlist per bride.
  - `WishlistItem` supports product, look, or salon favorites.

- `Order` / `OrderItem`
  - Tracks checkout orders and line items.
  - Includes GST, payment method, shipping address, and status.

- `UserPreference`
  - Stores bridal personalization data such as skin tone, face shape, wedding theme, and preferred colors.
  - Used by the recommendation engine.

- `BudgetPlan`
  - Records budget allocations across dresses, jewelry, makeup, accessories, and emergency buffer.

- `Notification`
  - Application-generated user notifications for orders, bookings, and system events.

- `AuditLog`
  - Stores structured audit events for important actions like product creation, booking confirmations, and status updates.

## Relationship Summary

- `User` has one `UserPreference`, one `BudgetPlan`, one `Wishlist`, many `Appointments`, many `Orders`, many `Reviews`, and many `Notifications`.
- `Category` has many `Product` records and self-referencing `subcategories`.
- `Product` belongs to one `Category` and can be favorited by many `WishlistItem` entries.
- `BridalLook` can be reviewed, booked, and wishlisted.
- `Salon` belongs to one `User` owner and contains multiple services, portfolio items, and appointments.
- `Appointment` joins `User`, `Salon`, and optionally `BridalLook`.
- `Order` owns many `OrderItem` records.
- `WishlistItem` provides a flexible favorite model for products, looks, or salons.

## Notes

- The model design optimizes role-specific workflows while keeping the schema extensible for additional bridal commerce features.
- The `sqlalchemy` relationships use cascading delete rules for clean data removal.
- `created_at` timestamps are available across major entities for auditability and reporting.

# 🛣️ API Routers (`/src/api`)

This directory contains the actual FastAPI "endpoints" (the URLs) that clients interact with. It acts as the Controller layer.

## What happens here?
Every file represents a distinct functional area of the bookstore. Inside each file, we define HTTP methods (`@router.get`, `@router.post`, etc.) and the core business logic.

*   `admin.py`: Aggregates complex analytics data and SQL queries for the Admin dashboard.
*   `auth.py`: Handles user registration, login, and issuing JSON Web Tokens (JWTs).
*   `books.py`: Controls the public catalog browsing, searching, and admin inventory management (CRUD logic).
*   `deps.py`: **Dependencies**. Reusable helper functions that FastAPI injects into routes (e.g., getting the database session or verifying if the current user is an Admin).
*   `favorites.py`: Manages customer wishlists.
*   `requisitions.py`: Handles placing stock restock orders to publishers and automated ordering logic.
*   `reviews.py`: Manages the 5-star customer ratings system.
*   `sales.py`: The checkout system! Handles cart management, dynamic pricing, and processing final orders.
*   `users.py`: Profile management endpoints (updating address, resetting passwords).

*Note: All of these individual routers are bundled together and initialized inside the central `src/main.py` file.*

## ⚡ API Optimizations & The "N+1 Problem"
This API layer has been explicitly optimized to prevent the **N+1 Query Problem**. 
When an endpoint needs to fetch a database model (like a `Book`) that contains a child relationship (like `Reviews`), a naive ORM implementation will run 1 query to get the book, and then *secretly* run an extra query for every single review attached to that book during JSON serialization. If you have 50 items, it runs 51 database queries instantly locking up the server.

If you browse files like `books.py`, you will notice we actively stop this by using SQLAlchemy's `joinedload()`. This is called **Eager Loading**, and it forces PostgreSQL to compute a single highly-optimized `JOIN` and return everything to the Python server in exactly *one* query. 

## ⚡ Background Processing 
Endpoints like `POST /requisitions/auto` use FastAPI's **BackgroundTasks**. Instead of freezing the server while the backend calculates 90 days of sales data for every book in the database, it immediately returns a `202 Accepted` response. A fresh database session is then spun up on a background worker thread (`process_auto_requisitions`) to handle the heavy lifting without blocking other customers from browsing the store!

## 📦 Memory-Safe Pagination
If an admin tries to load 100,000 old requisition orders, pulling all those SQL records into Python memory at once will crash Docker. To prevent this, data-heavy endpoints structurally incorporate strict **Server-Side Pagination** (`skip` and `limit`). By defaulting to yielding chunks of 50 items at a time, the backend RAM usage stays perfectly flat and predictable, regardless of how massive your database grows!

## 🛡️ API Rate Limiting (DDoS Protection)
The public-facing components of this API (such as the heavily-trafficked `GET /books/` catalog) are fortified with `SlowAPI`. We strictly enforce a limit of **60 requests per minute** per user IP address. This directly prevents malicious bots, scrapers, and DDoS attacks from spamming the API and intentionally crashing the database. If the limit is exceeded, FastAPI intercepts the request and safely returns a `429 Too Many Requests` error without ever executing the underlying logic.

## 🚀 In-Memory Caching
To achieve absolute maximum speed, heavy public endpoints are decorated with `@cache(expire=60)` from `fastapi-cache2`. The server remembers the exact database output of complex queries in ultra-fast RAM. If 5,000 customers open the "All Books" catalog within the same minute, PostgreSQL only executes the SQL search query exactly **1 time**. The other 4,999 requests are instantly served from the high-speed Python cache!

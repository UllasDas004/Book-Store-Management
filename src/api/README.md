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

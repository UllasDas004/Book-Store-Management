# 🛣️ API Routers (`/src/api`)

This directory contains the actual FastAPI "endpoints" (the URLs) that clients interact with. It acts as the Controller layer.

## What happens here?
Every file represents a distinct functional area of the bookstore. Inside each file, we define HTTP methods (`@router.get`, `@router.post`, etc.) and the core business logic.

*   `admin.py`: Aggregates complex analytics data and SQL queries for the Admin dashboard.
*   `auth.py`: Handles complex registration (auto-generating unique usernames by combining the user's `first_name` and `last_name`), strict plaintext password hashing, and injecting long-lasting, secure JWT tokens directly into browser 7-day cookies.
*   `books.py`: Controls the public catalog browsing, utilizing `.any()` for PostgreSQL category Array filtering, fuzzy search, and Admin CRUD powers.
*   `deps.py`: **Dependencies**. Reusable helper functions that FastAPI injects into routes (e.g., getting the database session or verifying if the current user is an Admin).
*   `favorites.py`: Manages customer wishlists safely.
*   `requisitions.py`: Handles placing stock restock orders and algorithmic background auto-ordering.
*   `reviews.py`: Manages the 5-star customer ratings system.
*   `sales.py`: The checkout system! Handles cart management, dynamic pricing discounts, and processing final immutable orders.
*   `users.py`: Profile management endpoints (updating granular name fields, address, resetting passwords).

*Note: All of these individual routers are bundled together and initialized inside the central `src/main.py` file.*

## ⚡ API Optimizations & The "N+1 Problem"
This API layer has been explicitly optimized to prevent the **N+1 Query Problem**. 
When an endpoint needs to fetch a database model that contains a child relationship (like `Reviews`), a naive ORM implementation will run 1 query to get the book, and then *secretly* run an extra query for every review attached to that book.

We actively stop this in two ways:
1.  **Schema Separation:** We strictly separate `BookResponse` from `BookDetailResponse`.
2.  **Eager Loading:** We use SQLAlchemy's `joinedload()` during `GET /books/{id}` to fetch everything structurally in a single SQL operation.

## 🛡️ Robust State Validations
The API layer actively defends against logic vulnerabilities such as the **"Infinite Cart Stock"** bypass. By dynamically calculating `existing_cart_quantity + incoming_quantity` *before* comparing against the database `stock_quantity`, the API mathematically prevents malicious users from tricking the system into selling more books than physically exist in the warehouse.

## ✨ Flexible Updates (PUT vs PATCH)
For modifying resources, the API implements both strict replacement (`PUT`) and flexible partial updates (`PATCH`). Using `exclude_unset=True` with Pydantic schemas, administrators can dynamically update a single field without having to transmit the entire payload.

## ⚡ Background Processing 
Endpoints like `POST /requisitions/auto` use FastAPI's **BackgroundTasks**. Instead of freezing the server while the backend calculates 90 days of sales data, it immediately returns a `202 Accepted` response, running the analytics query asynchronously behind the scenes.

## 📦 Memory-Safe Pagination
To prevent out-of-memory array crash loops, heavy endpoints structurally incorporate strict **Server-Side Pagination** (`skip` and `limit`). By yielding chunks of 50 items at a time, the backend RAM usage stays perfectly flat and predictable.

## 🛡️ API Rate Limiting (DDoS Protection)
The public-facing components of this API are fortified with `SlowAPI`. We strictly enforce a limit of **60 requests per minute** per user IP address natively rejecting automated bot scrapers with a `429 Too Many Requests` error.

## 🚀 In-Memory Caching
To achieve absolute maximum speed, heavy public endpoints are decorated with `@cache(expire=60)`. The server executes the complex SQL query once, stores the final stringified JSON output in server RAM, and serves identical traffic at a sub-millisecond response time!

## 🍪 Stateless Auto-Login (HttpOnly Cookies)
The API entirely bypasses standard JavaScript `localStorage` vulnerabilities by injecting the JSON Web Token (JWT) directly into a Secure, `HttpOnly` browser cookie during the `POST /auth/login` handshake. 
Because `HttpOnly` cookies are automatically attached by the browser to every subsequent request, the frontend React application simply fires a request to `GET /users/me` on initial page load to automatically "remember" and log in the user without prompting for credentials.

## 🕵️ Optional Dependencies (Silent RBAC)
For public endpoints that show dynamic content (like `GET /books/{id}`), the API implements advanced Optional Role-Based Access Control (RBAC). 
Using a custom FastAPI dependency (`get_current_user_optional` in `deps.py`), the endpoint quietly checks the cookie jar. If the user is unauthenticated, the system drops them into a Guest state without throwing aggressive `401 Unauthorized` errors. However, if the cookie reveals the user is an Admin, the very same endpoint dynamically unlocks restricted backend data (like viewing soft-deleted inventory).

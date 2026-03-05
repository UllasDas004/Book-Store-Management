# 📚 Bookstore Management System - Backend API

Welcome to the backend API for the Bookstore Management System! This is a robust, full-featured REST API built with FastAPI that handles everything a modern online bookstore needs: from customer shopping carts and secure checkouts to automated admin inventory restocks and sales analytics.

## 🚀 Tech Stack

*   **Framework:** FastAPI (High performance, easy to learn, fast to code, ready for production)
*   **Database:** PostgreSQL (Robust relational database)
*   **ORM:** SQLAlchemy (Object Relational Mapper for database interactions)
*   **Data Validation:** Pydantic (Type hints at runtime for robust payload validation)
*   **Authentication:** JWT (JSON Web Tokens) & OAuth2 Password Bearer
*   **Security:** Passlib (bcrypt) for secure password hashing
*   **Package Manager:** `uv` (Extremely fast Python package installer and resolver)

---

## ✨ Features & Functionality

This API is divided into two main roles: **Customers** (Standard Users) and **Admins** (Store Managers/Owners).

### 🔒 Authentication & Users (`/auth`, `/users`)
*   **Registration:** New users can sign up and implicitly receive the `customer` role.
*   **Login:** Secure login using `OAuth2PasswordRequestForm` returning a JWT access token valid for 30 minutes.
*   **Profile Management:** 
    *   Users can view their profile (`GET /users/me`).
    *   Users can update their address and phone number (`PUT /users/me`).
    *   Users can securely change their passwords (`PUT /users/me/password`).
*   **Admin Powers:** Admins can permanently delete user accounts (`DELETE /users/{user_id}`).

### 📖 Book Catalog (`/books`)
*   **Public Browsing:** Anyone (even unauthenticated users) can view the book catalog.
    *   Supports pagination (`skip`, `limit`).
    *   Supports dynamic fuzzy searching by **Title**, **Author**, or **ISBN** (using PostgreSQL `pg_trgm` extension for typo tolerance).
    *   Supports filtering by **Category**, **Min Price**, and **Max Price**.
    *   Supports sorting results via `sort_by` (`price_asc`, `price_desc`, `newest`).
*   **Detailed Views:** Fetching a single book (`GET /books/{id}`) automatically eager-loads and displays all user **reviews**.
*   **Admin Powers:**
    *   Add new books (`POST /books/`).
    *   Update book details like title, price, or applying a discount percentage (`PUT /books/{id}`).
    *   Upload high-quality book covers that are served statically (`POST /books/{id}/cover`).
    *   Delete books from the inventory (`DELETE /books/{id}`).

### 🛒 Shopping Cart & Checkout (`/sales`)
*   **Cart Management:**
    *   Add items to cart (`POST /sales/`). The API validates that sufficient `stock_quantity` exists before allowing the addition.
    *   View cart (`GET /sales/cart`). The API dynamically calculates the `total_price` based on current prices (and applies any active book discounts!).
    *   Update quantities in the cart (`PUT /sales/cart/{item_id}`). Setting quantity to `0` removes the item.
    *   Remove items from the cart (`DELETE /sales/cart/{item_id}`).
*   **Checkout:** 
    *   Process the entire cart (`POST /sales/sale`).
    *   The API uses SQLAlchemy `with_for_update()` to lock the book rows, preventing race conditions if two customers try to buy the last copy simultaneously!
    *   Upon successful checkout, stock is decremented, cart is cleared, and official `Sale` records are generated with a "Pending" status.
*   **Order History:** Customers can view their past orders and track their delivery status (`GET /sales/history`).
*   **Admin Powers:**
    *   Admins can update order statuses (e.g., from "Pending" to "Shipped" or "Delivered") (`PUT /sales/{sale_id}/status`).

### ⭐ Favorites & Reviews (`/favorites`, `/books/{id}/reviews`)
*   **Wishlists:** Customers can save books they are interested in for later (`POST /favorites/`).
*   **Reviews:** Customers can leave exactly *one* review (1-5 stars + optional comment) per book. The API actively prevents duplicate reviews from the same user to ensure fairness.

### 📈 Admin Dashboard & Analytics (`/admin`)
*   **Dashboard Stats:** An insanely fast endpoint (`GET /admin/dashboard`) designed for frontend UIs to display:
    *   Total system revenue.
    *   Total successful orders.
    *   Total registered customers and catalog size.
    *   Active low-stock alerts (books with `< 10` copies remaining).
*   **Advanced SQL Analytics:** 
    *   **Top 5 Best Selling Books:** Calculates lifetime copies sold.
    *   **Top 5 Highest Spending Customers:** Calculates lifetime revenue per user.

### 📦 Automated Inventory Requisitions (`/requisitions`)
*   **Manual Orders:** Admins can place a pending order to the publisher to restock specific books (`POST /requisitions/`).
*   **Smart Auto-Ordering:** 
    *   Admins can trigger `POST /requisitions/auto`.
    *   The API scans for any book dipping below `10` copies in stock.
    *   If a low-stock book has NO pending orders, the API calculates exactly how many copies of that book sold in the **last 3 months (90 days)**.
    *   It automatically drafts an order for exactly that many copies (or a default of 10 if it's a new book), ensuring the store never runs out of bestsellers!
*   **Receiving Inventory:** When the publisher delivers the books, Admins hit `PUT /requisitions/{id}/receive` to mark it complete and magically increment the `stock_quantity` in the store!

---

## 🏃‍♂️ How to Run the Project

1. **Prerequisites:** Ensure you have Python and `uv` installed. You also need a running PostgreSQL database.
2. **Environment Variables:** Setup your database URL in the `.env` file (if applicable) or ensure the database connection string in `src/db/database.py` is correct.
3. **Install Dependencies:**
   ```bash
   uv sync
   ```
4. **Start the Server:**
   ```bash
   uv run uvicorn src.main:app --reload
   ```
5. **View Documentation:**
   *   Open your browser and navigate to: `http://127.0.0.1:8000/docs`.
   *   FastAPI automatically generates an interactive Swagger UI where you can login, authenticate, and test every single endpoint right from your browser!

## 🔐 Default Setup Note
Since this backend uses Role-Based Access Control, you will need to manually change a user's `role` column from `"customer"` to `"admin"` in your Postgres database (e.g., via pgAdmin) for your very first admin account. After that, you can use the admin endpoints!

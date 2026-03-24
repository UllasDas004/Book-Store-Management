# 🗄️ Database Models (`/src/models`)

This directory contains **SQLAlchemy ORM** (Object-Relational Mapping) classes. 

## What happens here?
These Python classes directly represent the physical tables stored inside our PostgreSQL database. By defining relationships and columns here, SQLAlchemy automatically creates the database schema for us!

*   `book.py`: Defines the `Book` table. Implements the `admin_id` to track vendors. Crucially, the `category` attribute is implemented as a direct **PostgreSQL Array** for instantaneous multi-genre lookups.
*   `user.py`: Defines the `User` table. Tracks granular attributes like `first_name` and `last_name`, moving away from simple monolithic usernames, and handling hashed passwords globally.
*   `interaction.py`: Defines the actions users take with books:
    *   `CartItem`: Books currently sitting in a user's shopping cart.
    *   `Sale`: A completed checkout transaction.
    *   `Review`: A user's rating and comment for a book.
    *   `Favourite`: A relationship mapping a user to a book they want to save for later.
*   `requisition.py`: Defines the `Requisition` table (orders placed with publishers).

## 🛡️ Data Integrity & Soft Deletes
The models are structured to strictly enforce relational integrity. For example, if a customer purchases a book, a `Sale` record permanently points to that `book_id`. If an administrator tries to `DELETE` that book later, PostgreSQL would crash with a `ForeignKey IntegrityError`. 
To prevent this, the `Book` model implements an `is_active` boolean flag. Instead of destroying historical sales data, books are "Soft Deleted" by toggling this flag, seamlessly hiding them from the public catalog while keeping enterprise analytic data mathematically perfect.

## ⚡ Note on Performance & Indexing
If you look at the interaction models, you will notice that every single Foreign Key (`user_id` and `book_id`) is defined with `index=True`. 

**Why do we need this?**
Relational databases do not automatically index foreign keys! If we did not add `index=True`, PostgreSQL would have to read *every single row* in the `sales` table just to find the 3 books a specific user bought. By explicitly adding the index, we force the database to create a B-Tree lookup dictionary behind the scenes, ensuring that searching for a user's cart items or order history happens almost instantly ($O(\log n)$ time complexity).

## 📊 The 1NF Array Exemption
Inside `book.py`, `category` uses an explicit PostgreSQL `ARRAY(String)`. Note that while this technically violates First Normal Form (1NF) in strict traditional relational logic, modern post-relational database design explicitly encourages array denormalizations for read-heavy metadata architectures. This allows us to serve the frontend faster without an expensive multi-table join.

**Crucial Note:** These models are purely for interacting with the database. They are *not* the data we send directly to the internet. For inbound/outbound payload validation, see the `/src/schemas` directory.

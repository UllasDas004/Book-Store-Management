# 🗄️ Database Models (`/src/models`)

This directory contains **SQLAlchemy ORM** (Object-Relational Mapping) classes. 

## What happens here?
These Python classes directly represent the physical tables stored inside our PostgreSQL database. By defining relationships and columns here, SQLAlchemy automatically creates the database schema for us!

*   `book.py`: Defines the `Book` table (inventory items with price, stock, ISBN, etc.).
*   `user.py`: Defines the `User` table (handles both 'customer' and 'admin' roles, plus hashed passwords).
*   `interaction.py`: Defines the actions users take with books:
    *   `CartItem`: Books currently sitting in a user's shopping cart.
    *   `Sale`: A completed checkout transaction (a permanent receipt).
    *   `Review`: A user's rating and comment for a book.
    *   `Favourite`: A relationship mapping a user to a book they want to save for later.
*   `requisition.py`: Defines the `Requisition` table (orders placed with publishers to restock books).

## ⚡ Note on Performance & Indexing
If you look at the interaction models, you will notice that every single Foreign Key (`user_id` and `book_id`) is defined with `index=True`. 

**Why do we need this?**
Relational databases do not automatically index foreign keys! If we did not add `index=True`, PostgreSQL would have to read *every single row* in the `sales` table just to find the 3 books a specific user bought. If your store has 1 million sales, that single lookup would bring the server to a crawl. By explicitly adding the index, we force the database to create a B-Tree lookup dictionary behind the scenes, ensuring that searching for a user's cart items or order history happens almost instantly ($O(\log n)$ time complexity), no matter how large the database grows!

**Crucial Note:** These models are purely for interacting with the database. They are *not* the data we send directly to the internet. For inbound/outbound payload validation, see the `/src/schemas` directory.

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

**Crucial Note:** These models are purely for interacting with the database. They are *not* the data we send directly to the internet. For inbound/outbound payload validation, see the `/src/schemas` directory.

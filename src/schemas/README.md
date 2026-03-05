# 🛡️ Pydantic Schemas (`/src/schemas`)

This directory contains **Pydantic** classes used for robust data validation and serialization.

## What is a "Schema"?
While our `/models` folder dictates what goes into the **Database**, our `/schemas` folder dictates what comes over the **Internet** (the HTTP Requests and Responses).

These classes ensure that when a React frontend sends us data (like creating a new book), it provides *exactly* the fields we require with the correct data types (strings, integers, etc.). If the data is bad, FastAPI automatically rejects it with a 422 Unprocessable Entity error before our code even runs!

## Why separate Schemas and Models?
Security! When a user requests their profile data, our database `User` model contains their secret, hashed password. By forcing the database model to serialize through our `UserResponse` schema (which explicitly excludes the password field), we guarantee we will never accidentally leak sensitive data back to the frontend!

*   `book.py`: Schemas for creating/updating books and safely returning book data (including nested review schemas).
*   `interaction.py`: Schemas for carts, sales, wishlists, and publisher requisitions.
*   `user.py`: Schemas for user registration payloads, secure profile updates, and safe user responses.
*   `token.py`: Schemas specifically for the JWT authentication flow payloads.

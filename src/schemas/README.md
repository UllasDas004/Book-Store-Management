# 🛡️ Pydantic Schemas (`/src/schemas`)

This directory contains **Pydantic** classes used for robust data validation and serialization.

## What is a "Schema"?
While our `/models` folder dictates what goes into the **Database**, our `/schemas` folder dictates what comes over the **Internet** (the HTTP Requests and Responses).

These classes ensure that when a React frontend sends us data (like creating a new book), it provides *exactly* the fields we require with the correct data types. 

Furthermore, we heavily employ Pydantic's `Field` parameter to strictly enforce **Data Sanitization**:
*   Enforcing highly explicit minimum strings `min_length` (rejecting empty values) and specific bounds like `max_length=50` on the `ISBN` field to explicitly prevent payload crashes from abnormally long 16+ digit ISBN outputs provided by 3rd party providers like Google Books!
*   Enforcing bounds on integers (prices must be `gt=0`).
*   Configuring complex list constraints (e.g. `list[str]` array assertions for Book Categories).
*   Mandating `first_name` and `last_name` payload delivery while scrubbing internal data like auto-generated usernames.

If the data is bad, FastAPI automatically rejects it with a 422 Unprocessable Entity error instantly closing the physical memory buffer socket!

## Why separate Schemas and Models?
Security! When a user requests their profile data, our database `User` model contains their secret, hashed password. By forcing the database model to serialize through our `UserResponse` schema (which explicitly restricts output properties), we guarantee we will never leak sensitive attributes back to the client!

*   `book.py`: Schemas for creating/updating books safely, utilizing specific max string boundary limits for external ISBN API dependencies.
*   `interaction.py`: Schemas for complex transactional carts, sales tracking, and publisher requisitions.
*   `user.py`: Schemas for user registration payloads requiring proper First/Last names, and safe user responses.
*   `token.py`: Schemas tightly coupled with JWT payload definitions.

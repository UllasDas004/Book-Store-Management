# 🔌 Database Configuration (`/src/db`)

This folder manages the core connection tunnel between our Python backend and the PostgreSQL physical database.

*   `database.py`: 
    *   Creates the powerful SQLAlchemy `engine` that manages connection pooling.
    *   Configures the `SessionLocal` factory, which generates independent database sessions for every single API request.
    *   Defines the `Base` class that all of our models in `/src/models` inherit from.
    *   Provides the `get_db()` dependency function used widely in our API endpoints to securely yield and close database sessions upon completion.

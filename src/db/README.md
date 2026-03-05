# 🔌 Database Configuration (`/src/db`)

This folder manages the core connection tunnel between our Python backend and the PostgreSQL physical database.

*   `database.py`: 
    *   Creates the powerful SQLAlchemy `engine` that manages connection pooling.
    *   Configures the `SessionLocal` factory, which generates independent database sessions for every single API request.
    *   Defines the `Base` class that all of our models in `/src/models` inherit from.
*   Provides the `get_db()` dependency function used widely in our API endpoints to securely yield and close database sessions upon completion.

## 🚰 Connection Pooling (High Availability)
By default, if 1000 users hit your site simultaneously, SQLAlchemy tries to open 1000 literal connections to PostgreSQL, which causes the database to instantly crash with a "too many clients" fatal error. 

To prevent this, the `create_engine` call is strictly tuned:
*   `pool_size=20`: Keeps exactly 20 connections open at all times to instantly handle the majority of traffic without the latency of establishing new TCP connections.
*   `max_overflow=10`: If 20 people are currently querying, it temporarily accepts 10 more connections.
*   `pool_timeout=30`: If 30 people are querying, user #31 does not crash the app. They are smoothly queued and wait up to 30 seconds for a connection to become available!
*   `pool_pre_ping=True`: Ensures "stale/dropped" connections are quietly discarded instead of throwing internal server errors to the user.

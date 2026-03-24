# 🔌 Database Configuration (`/src/db`)

This directory manages the core connection tunnel and session lifecycle between our asynchronous FastAPI backend and the physical PostgreSQL database. It is fully configured for both local development and live cloud deployment (Render).

## 🗄️ Architecture Overview

Our backend employs a fully transactional, robust ORM approach leveraging **SQLAlchemy**:
*   `database.py`: 
    *   Instantiates the SQLAlchemy `engine`, mapping directly to the `DATABASE_URL` resolved dynamically in `/src/core/config.py`.
    *   Configures the `SessionLocal` factory. Every single API request calling `get_db()` receives a clean, totally isolated database transaction session to guarantee thread safety.
    *   Defines the declarative `Base` class, which all concrete models (`User`, `Book`, `Sale`, `Requisition`, etc.) inherit from to translate Python classes directly into PostgreSQL tables (`Base.metadata.create_all`).
*   **Dynamic Connectivity**: Through `pydantic-settings`, the system smartly falls back to individual components (`POSTGRES_USER`, `POSTGRES_HOST`) for local Docker development, but instantly accepts a monolithic `DATABASE_URL` string when pushed to Render's cloud architecture.

## 🚰 Connection Pooling (High Availability)

If your platform suddenly receives 1,000 simultaneous users (e.g. searching for a newly launched book category), opening 1,000 raw TCP socket connections to PostgreSQL would instantly cause the famous `too many clients already` fatal crash. 

To completely prevent latency spikes and crashing, the `create_engine` call in `database.py` is strictly tuned for enterprise loads:
*   `pool_size=20`: Keeps exactly 20 persistent, high-speed connections "warm" at all times to instantly manage HTTP throughput without connection-establishment latency.
*   `max_overflow=10`: During explosive traffic bursts, it dynamically allows 10 emergency overflow connections.
*   `pool_timeout=30`: This acts as a circuit breaker. If traffic maxes out the pool and overflow, the 31st user doesn't crash the server. They are elegantly queued and wait up to 30 seconds for a pooled connection to free up.
*   `pool_pre_ping=True`: A "pessimistic disconnect" handler. It sends an invisible ping before handing a session to a user to verify the database hasn't silently restarted, vastly reducing internal 500 server errors.

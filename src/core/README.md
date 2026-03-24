# ⚙️ Core Configuration & Security (`/src/core`)

This directory houses the central configuration settings and critical security utilities used globally across the backend.

*   `config.py`: Uses Pydantic's `BaseSettings` to load environment variables from a `.env` file or the system environment. 
    *   This file runs the highly crucial `assemble_db_connection` validator. It handles complex split-URI setups (for local Postgres docker instances with hosts/ports separated) but seamlessly allows `DATABASE_URL` monolith injection for seamless cloud deployments (like Render.com).
    *   It securely locks down token behavior, such as implementing the `ACCESS_TOKEN_EXPIRE_MINUTES: int = 7*24*60` variable to enforce robust **7-day persistence** for web-app logins.
*   `security.py`: The cryptographic brain of the application.
    *   Uses `bcrypt` to generate uncrackable password hashes and securely verify login attempts against them.
    *   Contains the core logic to encode, sign, and issue JSON Web Tokens (`create_access_token`) for modern stateless OAuth2 authentication configurations.

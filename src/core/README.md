# ⚙️ Core Configuration & Security (`/src/core`)

This directory houses the central configuration settings and critical security utilities used globally across the backend.

*   `config.py`: Uses Pydantic's `BaseSettings` to load environment variables (like the `DATABASE_URL` or secret keys) from a `.env` file or the system environment. This gives us type-hinted, validated application settings.
*   `security.py`: The cryptographic brain of the application.
    *   Uses `bcrypt` to generate uncrackable password hashes and securely verify login attempts against them.
    *   Contains the logic to encode, sign, and issue JSON Web Tokens (`create_access_token`) for stateless authentication.

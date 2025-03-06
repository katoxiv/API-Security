# API Security
(Case study: Calculator)

This Calculator API is a Flask-based web service that provides user authentication and the ability to evaluate mathematical expressions. The application is built with several extensions, including SQLAlchemy for database interactions, Flask-Login for user session management, Flask-Migrate for database migrations, and Flask-Limiter for rate limiting.

## Installation & Setup

Clone the repository:

```bash
git clone <repository_url>
cd calculator_API_Folder
```

Set up a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables:
- Ensure the environment file is correctly set up (e.g., with keys such as `SECRET_KEY`, `CALCULATE_LIMIT`, etc.).

## Configuration

The configuration is handled in two places:

- **myapp/config.py:** Defines the default settings such as the secret key, database URI, and rate limits.
- **Environment file (env):** May override default settings at runtime (for example, `CALCULATE_LIMIT=50/hour`).

## Authentication

User authentication is managed using Flask-Login and includes signup, login, and logout endpoints.

### Signup Endpoint

- **Route:** `/signup`
- **Method:** `POST`
- **Description:**
  - Uses the `RegistrationForm` to validate and sanitize input.
  - Checks for unique usernames.
  - Passwords are hashed before storage.
  - Rate-limited to 15 requests per day.
- **Response:**
  - On success: Returns a message and the new user's ID.
  - On failure: Returns error messages detailing the validation or database issues.

### Login Endpoint

- **Route:** `/login`
- **Method:** `POST`
- **Description:**
  - Uses the `LoginForm` to validate and sanitize input.
  - Verifies the username and password using the stored hash.
  - Rate-limited to 6 attempts per day.
  - Starts a session using Flask-Login on successful authentication.
- **Response:**
  - On success: Returns a message and the user's ID.
  - On failure: Returns an error indicating invalid credentials.

### Logout Endpoint

- **Route:** `/logout`
- **Method:** `GET`
- **Description:**
  - Logs out the currently authenticated user.
- **Response:**
  - Returns a message confirming the logout.

### Home Endpoint

- **Route:** `/`
- **Method:** `GET`
- **Description:**
  - Checks if a user is authenticated.
  - If authenticated, greets the user by username.
  - Otherwise, welcomes a guest.
- **Response:**
  - Returns an appropriate greeting message based on authentication status.

## Calculation Service

- **Route:** `/calculate`
- **Method:** `POST`
- **Description:**
  - Requires the user to be logged in.
  - Accepts a JSON payload with an `expression` key.
  - Validates the expression using a regular expression to prevent injection and ensure allowed characters.
  - Parses and evaluates the expression using Sympy.
  - Supports allowed functions such as `sqrt`, `sin`, `cos`, `tan`, `log`, `exp`, etc.
  - Formats the result, rounding to 2 decimal places or using scientific notation for very large or small numbers.
  - Rate-limited (configured to 50 calculations per hour via the environment variable).
- **Response:**
  - On success: Returns the evaluated result along with the current user's username.
  - On failure: Returns error details such as invalid input or evaluation errors.

## Error Handling

The application provides custom JSON responses for common HTTP errors:

- **400 Bad Request**
- **401 Unauthorized**
- **404 Not Found**
- **429 Rate Limiter exceeded**
- **500 Internal Server Error**

These handlers ensure that the client always receives a clear error message in JSON format.

## Running the Application

To start the application, run the `run.py` file:

```bash
python run.py
```

The server will start on [http://0.0.0.0:8080](http://0.0.0.0:8080).

## Database Migrations

The application uses Flask-Migrate with SQLAlchemy. To initialize and migrate the database, use the following commands:

```bash
flask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

## Rate Limiting

The app uses Flask-Limiter to prevent abuse:

- **Login attempts:** Limited to 6 per day.
- **Signup attempts:** Limited to 15 per day.
- **Calculation requests:** Limited to 50 per hour.

Rate limits are defined in the configuration and can be adjusted via the environment file.

## Security Considerations

- **Password Security:**  
  Passwords are never stored in plaintext; they are hashed using Werkzeug's security methods.

- **Input Sanitization:**  
  User inputs (e.g., usernames and passwords) are sanitized using Bleach to prevent malicious content.

- **Rate Limiting:**  
  Ensures that endpoints are not abused by limiting the number of requests per user.

- **Error Handling:**  
  Custom error handlers provide clear and consistent responses in case of invalid requests or server errors.

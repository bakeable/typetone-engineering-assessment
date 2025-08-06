# URL Shortening Service

## Overview

This is a URL shortening service built as part of a **Typetone engineering assessment**. The service provides functionality similar to TinyURL and bit.ly, allowing users to shorten long URLs with optional custom shortcodes, update existing URLs, and track usage statistics.

The complete assignment requirements can be found in [`typetone_assignment.pdf`](./typetone_assignment.pdf).

## Features

- 🔗 Shorten URLs with optional custom shortcodes
- ✏️ Update existing shortened URLs using update IDs
- 📊 Track redirect statistics (creation time, last redirect, redirect count)
- 🔄 Automatic redirect to original URLs
- ✅ Comprehensive test coverage
- 🚀 Built for scalability with clean, structured code

## Technology Stack

- **Python 3.9+**
- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Primary database for data persistence
- **SQLAlchemy** - Object-relational mapping (ORM)
- **Alembic** - Database migration tool
- **Poetry** - Dependency management and packaging
- **Pytest** - Testing framework with coverage reporting

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and route handlers
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic models for request/response validation
│   ├── database.py      # Database connection and session management
│   ├── crud.py          # Database operations (Create, Read, Update, Delete)
│   └── utils.py         # Utility functions (shortcode generation, validation)
├── tests/
│   └── test_main.py     # Comprehensive test suite
├── alembic/             # Database migration files
├── pyproject.toml       # Project configuration and dependencies
├── setup.sh            # Initial project setup script
└── README.md           # This file
```

## API Endpoints

### 1. **POST /shorten** - Shorten URL

Shortens a long URL with an optional custom shortcode.

**Request Body:**

```json
{
  "url": "https://www.example.com/very/long/url",
  "shortcode": "custom123" // Optional
}
```

**Response (201 Created):**

```json
{
  "shortcode": "custom123",
  "update_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses:**

- `409 Conflict` - Shortcode already exists
- `412 Precondition Failed` - Invalid shortcode format
- `422 Unprocessable Entity` - Invalid URL format

### 2. **POST /update/{update_id}** - Update URL

Updates the destination URL for an existing shortcode using the update ID.

**Request Body:**

```json
{
  "url": "https://www.updated-example.com"
}
```

**Response (201 Created):**

```json
{
  "shortcode": "custom123"
}
```

**Error Responses:**

- `401 Unauthorized` - Invalid update ID
- `412 Precondition Failed` - Invalid URL format
- `422 Unprocessable Entity` - Missing URL

### 3. **GET /{shortcode}** - Redirect to Original URL

Redirects to the original URL and increments the redirect counter.

**Response:**

- `302 Found` - Redirects to original URL
- `404 Not Found` - Shortcode doesn't exist

### 4. **GET /{shortcode}/stats** - Get URL Statistics

Retrieves statistics for a shortened URL.

**Response (200 OK):**

```json
{
  "created": "2025-08-06T10:30:00Z",
  "lastRedirect": "2025-08-06T15:45:30Z",
  "redirectCount": 42
}
```

**Error Responses:**

- `404 Not Found` - Shortcode doesn't exist

### 5. **GET /** - Service Information

Returns basic service information and API documentation link.

**Response (200 OK):**

```json
{
  "message": "URL Shortening Service",
  "version": "1.0.0",
  "docs": "/docs"
}
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database server
- Poetry package manager

### 1. Install Poetry (if not already installed)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 2. Setup the Environment

The project includes a setup script that initializes everything:

```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script (this will create the Poetry project and database)
./setup.sh
```

**Manual Setup (if needed):**

```bash
# Clone the repository
git clone <repository-url>
cd typetone-engineering-assessment

# Install dependencies
poetry install

# Setup PostgreSQL database
createdb url_shortener
psql -U postgres -c "CREATE USER myuser WITH PASSWORD 'mypass';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE url_shortener TO myuser;"

# Run database migrations
poetry run alembic upgrade head
```

### 3. Environment Configuration

Create a `.env` file in the project root (optional - defaults are provided):

```env
DATABASE_URL=postgresql://myuser:mypass@localhost:5432/url_shortener
```

## Running the Application

### Start the Development Server

```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at:

- **API**: http://localhost:8000
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc

### Production Deployment

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Tests

### Run All Tests with Coverage

```bash
poetry run pytest --cov=app --cov-report=term-missing
```

## License

This project was created as part of a Typetone engineering assessment.

#!/bin/bash
set -e 

# Config
PROJECT_NAME="url_shortener"
AUTHOR_NAME="Robin Bakker"
AUTHOR_EMAIL="robin@bakeable.nl"


# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo -e "Poetry not found. Please install Poetry to manage dependencies."
    exit 1
fi

# Init Poetry project
poetry init --name "$PROJECT_NAME" \
           --description "An URL shortening service built with FastAPI and PostgreSQL" \
           --author "$AUTHOR_NAME <$AUTHOR_EMAIL>" \
           --python "^3.9" \
           --no-interaction

# Add dependencies
poetry add fastapi "uvicorn[standard]" sqlalchemy psycopg2-binary pydantic python-dotenv alembic
poetry add --group dev pytest pytest-asyncio httpx pytest-cov

# Create directory structure
mkdir -p app tests alembic/versions .vscode

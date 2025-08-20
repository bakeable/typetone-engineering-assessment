
migrate:
	poetry run alembic upgrade head

test:
	poetry run pytest --cov=app --cov-report=term-missing --disable-warnings

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
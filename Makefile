
migrate:
	poetry run alembic upgrade head

test:
	poetry run pytest --cov=typetone --cov-report=term-missing
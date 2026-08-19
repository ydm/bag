.PHONY: db db-stop test run

db:
	docker compose up -d

db-stop:
	docker compose down

test:
	cd app && .venv/bin/pytest

run:
	cd app && .venv/bin/uvicorn main:app --reload

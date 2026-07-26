.PHONY: up test lint fmt fill sh

up:
	docker compose up --build

test:
	docker compose run --rm app pytest

lint:
	docker compose run --rm app ruff check .

fmt:
	docker compose run --rm app ruff format .

fill:
	docker compose run --rm app python -m apps.dev_fill

sh:
	docker compose run --rm app bash

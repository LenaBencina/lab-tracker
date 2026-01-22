.PHONY: install lint format test clean

install:
	uv sync
	uv run pre-commit install

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

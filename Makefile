init:
	uv sync --dev

format:
	uv run ruff format && uv run ruff check . --fix

test: format
	uv run pytest
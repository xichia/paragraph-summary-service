.PHONY: install dev test lint run docker-build clean
install:
	python3 -m pip install -e .
dev:
	python3 -m pip install -e ".[dev]"
test:
	python3 -m pytest
lint:
	python3 -m ruff check src tests
run:
	uvicorn paragraph_summary_service.api.app:create_app --factory --reload
docker-build:
	docker build -t paragraph-summary-service .
clean:
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage output .local

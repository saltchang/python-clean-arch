.PHONY: analyze-dependencies lint format type-check run-unit-tests clean check-all init-db reset-db

PYTHON_PATH = PYTHONPATH=./app:./tests
TEST_ENV = ENV_FILE=.env.test $(PYTHON_PATH)
APP_PYTHON_PATH = PYTHONPATH=./app
COVERAGE_PATHS = --cov=app/api --cov=app/core --cov=app/repository --cov=app/service --cov=app/utility

# Analyze Dependencies
analyze-dependencies:
	@echo "Analyzing dependencies..."
	$(APP_PYTHON_PATH) pydeps ./app

# Run Server
run-server:
	@echo "Running the server..."
	$(APP_PYTHON_PATH) poetry run uvicorn app.main:http_api_app --reload --port 7086 --host 0.0.0.0

# Run the unit tests
run-unit-tests:
	@echo "Running unit tests..."
	$(TEST_ENV) pytest tests/unit $(COVERAGE_PATHS)

# Clean up build artifacts and cache
clean:
	@echo "Cleaning up..."
	find . -type d -name '__pycache__' -exec rm -r {} +
	find . -type d -name '.ruff_cache' -exec rm -r {} +
	find . -type d -name '.pytest_cache' -exec rm -r {} +

# Lint the code using Ruff
lint:
	@echo "Linting the code..."
	$(PYTHON_PATH) poetry run ruff check .

# Format the code using Ruff
format:
	@echo "Formatting the code..."
	$(PYTHON_PATH) poetry run ruff format .

# Type-check the code using Pyright
type-check:
	@echo "Type-checking the code..."
	$(PYTHON_PATH) poetry run pyright

# Check all
check-all:
	@echo "Checking all..."
	make clean
	make lint
	make format
	make type-check
	make run-unit-tests

# Initialize database
init-db:
	@echo "Initializing database..."
	ENV_FILE=.env ./scripts/init_db_pg.sh init

# Reset database to initial state
reset-db:
	@echo "Resetting database..."
	ENV_FILE=.env ./scripts/init_db_pg.sh reset

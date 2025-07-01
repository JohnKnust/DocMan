# DocMan - Documentation Management CLI Tool
# Makefile for development, testing, and maintenance tasks

# Variables
PYTHON := python
PIP := pip
VENV_ACTIVATE := . ../../.python-version
SRC_DIR := src
TEST_DIR := tests
CLI_SCRIPT := cli.py

# Default target
.PHONY: help
help:
	@echo "DocMan - Documentation Management CLI Tool"
	@echo ""
	@echo "Available targets:"
	@echo "  install          - Install dependencies"
	@echo "  generate-examples- Generate example repository structure"
	@echo "  check-syntax     - Check Python syntax"
	@echo "  run              - Run DocMan on current directory"
	@echo "  run-fix          - Run DocMan with auto-fix enabled"
	@echo "  run-verbose      - Run DocMan with verbose output"
	@echo "  run-report       - Run DocMan with detailed report"
	@echo "  run-examples     - Generate examples and run DocMan on them"
	@echo "  validate         - Run all validation checks"
	@echo "  test             - Run unit tests"
	@echo "  lint             - Run linting checks"
	@echo "  format           - Format code with black"
	@echo "  type-check       - Run type checking with mypy"
	@echo "  clean            - Clean up temporary files"
	@echo "  quick-check      - Run quick syntax and basic tests"

# Install dependencies
.PHONY: install
install:
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install pytest black flake8 mypy

# Check Python syntax
.PHONY: check-syntax
check-syntax:
	@echo "🔍 Checking Python syntax..."
	$(PYTHON) -m py_compile $(CLI_SCRIPT)
	$(PYTHON) -m py_compile $(SRC_DIR)/*.py
	$(PYTHON) -m py_compile $(SRC_DIR)/validators/*.py
	$(PYTHON) -m py_compile $(TEST_DIR)/*.py

# Generate example structure
.PHONY: generate-examples
generate-examples:
	@echo "🎨 Generating example structure..."
	$(PYTHON) generate_examples.py

# Run DocMan on current directory
.PHONY: run
run:
	@echo "🚀 Running DocMan..."
	$(PYTHON) $(CLI_SCRIPT)

# Run DocMan with auto-fix enabled
.PHONY: run-fix
run-fix:
	@echo "🔧 Running DocMan with auto-fix..."
	$(PYTHON) $(CLI_SCRIPT) --fix

# Run DocMan with verbose output
.PHONY: run-verbose
run-verbose:
	@echo "📝 Running DocMan with verbose output..."
	$(PYTHON) $(CLI_SCRIPT) --verbose

# Run DocMan with detailed report
.PHONY: run-report
run-report:
	@echo "📊 Running DocMan with detailed report..."
	$(PYTHON) $(CLI_SCRIPT) --report

# Run DocMan on generated examples
.PHONY: run-examples
run-examples: generate-examples
	@echo "🧪 Running DocMan on generated examples..."
	$(PYTHON) $(CLI_SCRIPT) examples/samplerepo --verbose

# Run all validation checks
.PHONY: validate
validate: check-syntax lint type-check
	@echo "✅ All validation checks completed"

# Run unit tests
.PHONY: test
test:
	@echo "🧪 Running unit tests..."
	$(PYTHON) -m pytest $(TEST_DIR) -v

# Run linting checks
.PHONY: lint
lint:
	@echo "🔍 Running linting checks..."
	flake8 $(SRC_DIR) $(TEST_DIR) $(CLI_SCRIPT) --max-line-length=88 --extend-ignore=E203,W503

# Format code with black
.PHONY: format
format:
	@echo "🎨 Formatting code..."
	black $(SRC_DIR) $(TEST_DIR) $(CLI_SCRIPT) --line-length=88

# Run type checking with mypy
.PHONY: type-check
type-check:
	@echo "🔍 Running type checks..."
	mypy $(SRC_DIR) $(CLI_SCRIPT) --ignore-missing-imports

# Clean up temporary files
.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.log" -delete

# Quick check for development
.PHONY: quick-check
quick-check: check-syntax test
	@echo "⚡ Quick check completed"

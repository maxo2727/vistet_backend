# VisteT Backend - Linting and Formatting Commands
# Usage: make lint, make format, make check

.PHONY: help lint format check fix install-dev test

help:  ## Show this help message
	@echo "Available commands:"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make lint        - Run all linting checks"
	@echo "  make format      - Format all Python files" 
	@echo "  make check       - Check code without making changes"
	@echo "  make fix         - Auto-fix all issues that can be fixed"

install-dev:  ## Install development dependencies
	pip install -r requirements.txt

lint:  ## Run all linting checks
	@echo "🔍 Running flake8 linter..."
	flake8 .
	@echo "📋 Checking import order..."
	isort --check-only --diff .
	@echo "🎨 Checking code formatting..."
	black --check .
	@echo "✅ All linting checks completed!"

format:  ## Format all Python files
	@echo "📋 Sorting imports..."
	isort .
	@echo "🎨 Formatting code with black..."
	black .
	@echo "✅ Code formatting completed!"

check:  ## Check code without making changes
	@echo "🔍 Checking code style..."
	flake8 .
	isort --check-only .
	black --check .

fix:  ## Auto-fix all issues that can be fixed
	@echo "🔧 Auto-fixing issues..."
	@echo "📋 Sorting imports..."
	isort .
	@echo "🎨 Formatting code with black..."
	black .
	@echo "🧹 Removing trailing whitespace..."
	find . -name "*.py" -exec sed -i 's/[[:space:]]*$$//' {} \;
	@echo "✅ Fixed all auto-fixable issues!"

# Check for commented code (your specific request!)
check-comments:
	@echo "🔍 Checking for commented code..."
	@grep -r "^[[:space:]]*#[[:space:]]*[a-zA-Z]" --include="*.py" . | grep -v "# " | head -10 || echo "✅ No commented code found!" 
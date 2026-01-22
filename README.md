# Python Project Template

A template repository for Python projects using `uv` and `ruff`.

## Setup

1. Click "Use this template" to create a new repository
2. Clone your new repository
3. Update `pyproject.toml` with your project name and details
4. Run: `make install` (or `uv sync` and `uv run pre-commit install`)
5. Start coding!

## Tools Included

- **uv**: Fast Python package installer and resolver
- **ruff**: Fast Python linter and formatter (pre-configured)
- **pre-commit**: Git hook manager (pre-configured)
- **pytest**: Testing framework

## Usage

### With Make (recommended)
```bash
make install    # Install dependencies and pre-commit hooks
make lint       # Run linting
make format     # Run formatting
make test       # Run tests
make clean      # Clean up cache files
```

### Without Make
```bash
# Install/sync all dependencies
uv sync

# Add new dependencies
uv add <package>

# Add dev dependencies
uv add --dev <package>

# Run linting
uv run ruff check .

# Run formatting
uv run ruff format .

# Run tests
uv run pytest

# Run pre-commit on all files
uv run pre-commit run --all-files
```

## Project Structure

Update `pyproject.toml` with your project-specific information:
- Project name
- Description
- Author
- Python version requirements

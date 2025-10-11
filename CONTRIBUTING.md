# Contributing to TFModSearch MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/aws-tf-modules-mcp-server.git
   cd aws-tf-modules-mcp-server
   ```

3. Set up development environment:
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes following the code style guidelines

3. Run tests and quality checks:
   ```bash
   # Run all tests
   pytest tests/ -v

   # Run type checker
   mypy src/

   # Run linter and formatter
   ruff check src/ tests/
   ruff format src/ tests/

   # Or run all checks at once
   pre-commit run --all-files
   ```

4. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

5. Push to your fork and create a Pull Request

## Code Style Guidelines

- Follow PEP 8 style guidelines (enforced by `ruff`)
- Add type hints to all functions (checked by `mypy`)
- Write docstrings for public functions and classes
- Keep line length to 120 characters
- Use meaningful variable and function names

## Commit Message Convention

We use conventional commit messages:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding or updating tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example: `feat: add support for custom embeddings models`

## Testing Guidelines

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Use descriptive test names that explain what is being tested

## Pull Request Process

1. Update documentation if you're adding features
2. Ensure all tests pass and code quality checks succeed
3. Update the README.md if needed
4. Provide a clear description of the changes in your PR
5. Link any related issues

## Questions or Issues?

- Open an issue for bugs or feature requests
- Use discussions for questions and ideas
- Be respectful and constructive in all interactions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

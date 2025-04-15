# CLAUDE.md - Development Guidelines

## Commands
- Run server: `python manage.py runserver`
- Run tests: `python manage.py test`
- Run specific test: `python manage.py test chat.tests.TestCaseName.test_method_name`
- Lint code: `flake8 selist/`
- Django shell: `python manage.py shell`
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`

## Code Style
- PEP 8 guidelines
- 4-space indentation
- Double quotes for strings
- Line length <= 100 characters
- Import order: standard library, third-party, local apps
- Models: explicit field types, include `__str__` methods
- Foreign keys: use PROTECT for on_delete
- Use type hints where appropriate
- Error handling: specific exceptions with descriptive messages
- Naming: snake_case for functions/variables, CamelCase for classes

## Project Structure
- Django project with chat functionality
- Uses SQLite database by default
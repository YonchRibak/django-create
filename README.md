# django-create

`django-create` is a CLI tool designed to streamline the development process in Django projects. This tool helps developers automatically generate Django models, views, serializers, viewsets, and tests from templates, as well as organize Django apps into structured folders.

## Features

- **File Template Creation**: Quickly generate Django models, views, serializers, viewsets, and test files with CLI commands.
- **Folder Structure Management**: Automatically organize your Django app into standard folders (`models`, `views`, `viewsets`, and `tests`).
- **Extract Class Definitions**: Extract class definitions from existing files (like `models.py`, `views.py`) and move them into individual files inside organized folders.
- **Contextual Management**: Each command works within the context of an app to create and organize files efficiently.
- **Auto-Generated Imports**: Ensures imports are added to the `__init__.py` files in each folder, allowing seamless module access across your project.

## Installation

To install `django-create` locally without publishing it to PyPI:

```bash
# Build the package
poetry build

# Install locally
poetry run pip install path/to/your/package/dist/django_create-0.1.0-py3-none-any.whl


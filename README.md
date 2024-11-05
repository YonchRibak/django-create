# Django Create

A powerful CLI tool for organizing and maintaining Django applications with a focus on scalability and code organization.

## Overview

Django Create helps you maintain clean and organized Django applications by providing tools to:

- Create and organize Django models, views, serializers, viewsets, and tests
- Convert single-file modules into organized directory structures
- Maintain consistent import statements and file organization
- Support nested directory structures for complex applications

## Installation

```bash
# Using pip
pip install django-create

# Using Poetry
poetry add django-create
```

## Usage

### Basic Commands

The basic structure of commands is:

```bash
django-create <app_name> <command> <element_name> [options]
```

#### Creating New Elements

Create new Django elements with automatic file organization:

```bash
# Create a new model
django-create myapp create model UserProfile

# Create a new view
django-create myapp create view UserListView

# Create a new serializer with associated model
django-create myapp create serializer UserSerializer --model User

# Create a new viewset with model and serializer
django-create myapp create viewset UserViewSet --model User --serializer UserSerializer

# Create a new test
django-create myapp create test UserTest
```

#### Organizing Elements in Subdirectories

You can organize elements in subdirectories using the `--path` option:

```bash
# Create a model in a subdirectory
django-create myapp create model ProductVariant --path products/variants

# Create a view in a subdirectory
django-create myapp create view ProductListView --path products/lists
```

### Folderizing an App

The `folderize` command converts a Django app from single-file modules to an organized directory structure:

```bash
django-create myapp folderize
```

This command:
1. Creates appropriate directories (`models/`, `views/`, `serializers/`, etc.)
2. Extracts classes from single files into individual modules
3. Updates import statements automatically
4. Creates `__init__.py` files with correct imports
5. Removes the original single files

For example, `models.py` containing multiple models would be split into:
```
models/
├── __init__.py
├── user.py
├── profile.py
└── settings.py
```

## Directory Structure

After using folderize command, your app structure might look like this:

```
myapp/
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── profile.py
├── views/
│   ├── __init__.py
│   ├── user_views.py
│   └── profile_views.py
├── serializers/
│   ├── __init__.py
│   ├── user_serializer.py
│   └── profile_serializer.py
├── viewsets/
│   ├── __init__.py
│   ├── user_viewset.py
│   └── profile_viewset.py
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_views.py
```

## Features

- **Automatic Import Management**: Correctly handles relative imports and updates `__init__.py` files
- **Nested Directory Support**: Create and maintain complex directory structures
- **Template-Based Generation**: Consistent file creation using predefined templates
- **Smart File Organization**: Converts single-file modules into organized directories
- **Import Statement Optimization**: Merges and organizes import statements efficiently
- **Conflict Prevention**: Prevents issues with duplicate files/folders
- **Clean Migration**: Safely moves from single-file to directory structure

## Best Practices

1. **Use Descriptive Names**: Name your elements clearly (e.g., `UserProfileSerializer` instead of just `Serializer`)
2. **Organize Related Components**: Use the `--path` option to group related components
3. **Folderize Early**: Convert to directory structure early in development
4. **Maintain Structure**: Continue using the CLI tools after folderizing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing

To run the test suite:

```bash
pytest
```

## License

MIT License - see the [LICENSE](LICENSE) file for details

## Support

If you encounter any issues or have questions, please:

1. Check the existing issues on GitHub
2. Create a new issue if needed
3. Provide detailed information about your environment and the problem

## Future Plans

- Add support for DRF generic views
- Include customizable templates
- Add support for Django signals
- Implement database migration helpers
- Add support for Django admin customization

## Credits

Created and maintained by Jonathan Ribak.
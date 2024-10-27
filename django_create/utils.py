import os
import re
import click
from pathlib import Path

def render_template(template_path, **kwargs):
    """
    Reads a template file and replaces placeholders with provided values.
    """
    with open(template_path, 'r') as file:
        content = file.read()

    # Replace placeholders in the content with the provided keyword arguments
    for key, value in kwargs.items():
        placeholder = f"{{{{ {key} }}}}"
        content = content.replace(placeholder, value)

    return content

def save_rendered_template(content, output_path):
    """
    Saves rendered template content to the specified output path.
    """
    with open(output_path, 'w') as file:
        file.write(content)

def snake_case(text):
    """
    Convert text to snake_case, handling special cases.
    Examples:
        ProductViewSet -> product_viewset
        TestViewSetWithoutImport -> test_viewset_without_import
        Already_Snake_Case -> already_snake_case
        UserProfile -> user_profile
    """
    # Handle ViewSet special case anywhere in the text
    text = text.replace('ViewSet', 'Viewset')
    
    # If text contains underscores, just convert to lowercase
    if '_' in text:
        return text.lower()
    
    # Regular snake_case conversion for camelCase/PascalCase
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    
    # Replace 'viewset' with 'viewset' to ensure consistent casing
    final = s2.lower().replace('view_set', 'viewset')
    
    return final
def inject_element_into_file(file_path, element_content):
    """
    Injects the given element content into an existing file without altering other content.
    
    Used for adding a new model, view, or serializer to an existing file like models.py.
    """
    with open(file_path, 'a') as f:
        f.write("\n\n" + element_content)

    click.echo(f"Injected content into '{file_path}'.")

def create_element_file(element_file_path, element_content):
    """
    Create a file with the specified content at the given path, ensuring the directory exists.
    """
    # Convert element_file_path to a Path object if it's a string
    element_file_path = Path(element_file_path)
    
    # Ensure the parent directory exists
    element_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    save_rendered_template(element_content, element_file_path)

def add_import_to_file(init_file_path, element_name, element_file_name):
    """
    Adds an import statement to a specified file (e.g., models/__init__.py) for the new element.
    
    Can be used to add imports for models, views, serializers, etc.
    """
    import_statement = f"from .{element_file_name[:-3]} import {element_name}\n"
    
    # Ensure __init__.py exists
    os.makedirs(os.path.dirname(init_file_path), exist_ok=True)
    if not os.path.exists(init_file_path):
        with open(init_file_path, 'w') as f:
            f.write("# Imports for Django elements\n")

    # Check if the import already exists
    with open(init_file_path, 'r') as f:
        init_content = f.read()

    if import_statement not in init_content:
        with open(init_file_path, 'a') as f:
            f.write(import_statement)
        click.echo(f"Added import to '{init_file_path}': {import_statement.strip()}")

def create_mock_django_app(
    tmp_path, 
    app_name='myapp', 
    with_models_file=True, 
    with_views_file=True,
    with_viewsets_file=True,
    with_serializers_file=True,
    with_tests_file=True,
    with_models_folder=False, 
    with_views_folder=False, 
    with_viewsets_folder=False, 
    with_serializers_folder=False, 
    with_tests_folder=False,
    subdirectory=None
):
    """
    Creates a mock Django app directory structure for testing.
    
    Parameters:
    - tmp_path: A pytest fixture for creating temporary directories.
    - app_name: The name of the mock Django app.
    - with_models_file: Whether to include a models.py file in the app.
    - with_models_folder: Whether to include a models/ folder in the app.
    - with_views_folder: Whether to include a views/ folder in the app.
    - with_viewsets_folder: Whether to include a viewsets/ folder in the app.
    - with_serializers_folder: Whether to include a serializers/ folder in the app.
    - with_tests_folder: Whether to include a tests/ folder in the app.
    
    Returns:
    - Path to the mock app.
    """
    
    base_path = tmp_path / subdirectory if subdirectory else tmp_path
    base_path.mkdir(parents=True, exist_ok=True)
    app_path = base_path / app_name
    app_path.mkdir(parents=True, exist_ok=True)

    # Create models.py if requested
    if with_models_file:
        models_py = app_path / 'models.py'
        models_py.write_text("# models.py file for testing\n")

    # Create views.py if requested
    if with_views_file:
        views_py = app_path / 'views.py'
        views_py.write_text("# views.py file for testing\n")

    # Create viewsets.py if requested
    if with_viewsets_file:
        viewsets_py = app_path / 'viewsets.py'
        viewsets_py.write_text("# viewsets.py file for testing\n")

    # Create serializers.py if requested
    if with_serializers_file:
        serializers_py = app_path / 'serializers.py'
        serializers_py.write_text("# serializers.py file for testing\n")
    
    # Create tests.py if requested
    if with_tests_file:
        tests_py = app_path / 'tests.py'
        tests_py.write_text("# tests.py file for testing\n")

    # Create models folder if requested
    if with_models_folder:
        models_folder = app_path / 'models'
        models_folder.mkdir(parents=True, exist_ok=True)
        (models_folder / '__init__.py').write_text("# models/__init__.py for testing\n")

    # Create views folder if requested
    if with_views_folder:
        views_folder = app_path / 'views'
        views_folder.mkdir(parents=True, exist_ok=True)
        (views_folder / '__init__.py').write_text("# views/__init__.py for testing\n")

    # Create viewsets folder if requested
    if with_viewsets_folder:
        viewsets_folder = app_path / 'viewsets'
        viewsets_folder.mkdir(parents=True, exist_ok=True)
        (viewsets_folder / '__init__.py').write_text("# viewsets/__init__.py for testing\n")

    # Create serializers folder if requested
    if with_serializers_folder:
        serializers_folder = app_path / 'serializers'
        serializers_folder.mkdir(parents=True, exist_ok=True)
        (serializers_folder / '__init__.py').write_text("# serializers/__init__.py for testing\n")

    # Create tests folder if requested
    if with_tests_folder:
        tests_folder = app_path / 'tests'
        tests_folder.mkdir(parents=True, exist_ok=True)
        (tests_folder / '__init__.py').write_text("# tests/__init__.py for testing\n")
        (tests_folder / 'test_sample.py').write_text("# Sample test file for testing\n")

    return app_path

def is_import_in_file(file, import_txt) -> bool:
    """
    Check if necessary import statement is present in file.
    """
    with open(file, 'r') as file:
        content = file.read()
        return import_txt in content
    

def extract_file_contents(file_path):
    """
    Extracts imports and top-level class definitions from a file.
    Returns a dictionary with 'imports' as one key and each top-level class name as additional keys.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all imports (lines starting with 'import' or 'from')
    imports = "\n".join(re.findall(r'^(?:from|import) .+', content, re.MULTILINE))

    # Extract each top-level class
    classes = {}
    # Split content into lines for processing
    lines = content.split('\n')
    current_class = None
    current_content = []
    indent_level = 0

    for line in lines:
        # Check for class definition
        class_match = re.match(r'^class\s+(\w+)\s*.*:', line)
        
        if class_match:
            # If we were processing a previous class, save it
            if current_class:
                classes[current_class] = '\n'.join(current_content)
            
            # Start new class
            current_class = class_match.group(1)
            current_content = [line]
            indent_level = len(line) - len(line.lstrip())
            continue

        # If we're currently processing a class
        if current_class:
            # Empty lines are included if we're in a class
            if not line.strip():
                current_content.append(line)
                continue

            # Check if this line is part of the current class
            current_indent = len(line) - len(line.lstrip())
            if not line.strip() or current_indent > indent_level:
                current_content.append(line)
            else:
                # This line is not part of the class, save current class and reset
                classes[current_class] = '\n'.join(current_content)
                current_class = None
                current_content = []

    # Save the last class if we were processing one
    if current_class:
        classes[current_class] = '\n'.join(current_content)

    return {"imports": imports, **classes}

def contains_class_definition(file_path):
    """
    Check if a file contains any class definitions.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Look for any class definitions using a regex pattern
        return re.search(r'^\s*class\s+\w+', content, re.MULTILINE) is not None

def find_app_path(app_name):
    """
    Search for the app_name folder in the current directory and its subdirectories.
    """
    for root, dirs, _ in os.walk(os.getcwd()):
        if app_name in dirs:
            return os.path.join(root, app_name)
    return None
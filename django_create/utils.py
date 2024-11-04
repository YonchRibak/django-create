import os
import re
import click
from pathlib import Path

class Utils:
    DJANGO_IMPORTS = {
        'models': 'from django.db import models',
        'views': 'from django.views import View',
        'serializers': 'from rest_framework import serializers',
        'viewsets': 'from rest_framework import viewsets',
        'tests': 'from django.test import TestCase',
        'admin': 'from django.contrib import admin'
    }

    DEFAULT_COMMENTS = {
        'models': '# Create your models here',
        'views': '# Create your views here',
        'serializers': '# Create your serializers here',
        'viewsets': '# Create your viewsets here',
        'tests': '# Create your tests here',
        'admin': '# Register your models here'
    }

    STANDARD_MODULES = ['models', 'views', 'serializers', 'viewsets', 'tests']

    @classmethod
    def is_default_content(cls, file_path, file_type):
        """
        Check if file only contains Django's default content.
        Handles variations in whitespace and ordering.
        
        Args:
            file_path: Path to the file to check
            file_type: Type of file ('models', 'views', etc.)
            
        Returns:
            bool: True if file only contains default content
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
            # Get the expected elements
            expected_import = cls.DJANGO_IMPORTS.get(file_type, '')
            expected_comment = cls.DEFAULT_COMMENTS.get(file_type, '')

            expected_content = '\n'.join([expected_import, expected_comment])

            return content == expected_content
        except Exception:
            return False

    @classmethod
    def determine_import_style(cls, app_path, module_type):
        """
        Determine whether to use dot (.) or dotdot (..) style imports.
        
        Args:
            app_path: Path to the Django app
            module_type: Type of module ('models', 'serializers', etc.)
            
        Returns:
            str: 'dot' or 'dotdot'
        """
        if not module_type or module_type not in cls.STANDARD_MODULES:
            return 'dot'

        module_folder = app_path / module_type
        return 'dotdot' if module_folder.exists() else 'dot'

    @classmethod
    def process_template_imports(cls, content, app_path):
        """
        Process template content to use correct import style based on app structure.
        
        Args:
            content: Template content to process
            app_path: Path to Django app
            
        Returns:
            str: Processed content with correct import paths
        """
        if not content:
            return content

        # Create mapping of import styles for each module type
        import_styles = {
            module: cls.determine_import_style(app_path, module)
            for module in cls.STANDARD_MODULES
        }

        # Process each line
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            processed_line = line
            
            # Check for imports to modify
            for module in cls.STANDARD_MODULES:
                if f'from .{module}' in line:
                    if import_styles[module] == 'dotdot':
                        processed_line = line.replace(f'from .{module}', f'from ..{module}')
                elif f'from ..{module}' in line:
                    if import_styles[module] == 'dot':
                        processed_line = line.replace(f'from ..{module}', f'from .{module}')
            
            processed_lines.append(processed_line)

        return '\n'.join(processed_lines)

    @classmethod
    def render_template(cls, template_path, app_path, **kwargs):
        """
        Render a template with correct imports based on app structure.
        
        Args:
            template_path: Path to template file
            app_path: Path to Django app
            **kwargs: Template variables
            
        Returns:
            str: Rendered template content
        """
        try:
            with open(template_path, 'r') as f:
                content = f.read()

            # First replace template variables
            for key, value in kwargs.items():
                content = content.replace(f"{{{{ {key} }}}}", str(value))

            # Then process imports
            content = cls.process_template_imports(content, app_path)

            return content
        except Exception as e:
            raise ValueError(f"Error rendering template: {str(e)}")

    @classmethod
    def should_overwrite_file(cls, file_path, file_type):
        """
        Determine if a file should be overwritten based on its content.
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('models', 'views', etc.)
            
        Returns:
            bool: True if file should be overwritten
        """
        if not file_path.exists():
            return True
            
        return cls.is_default_content(file_path, file_type)

    @classmethod
    def write_or_append_content(cls, file_path, content, content_type):
        """Write content to a file, either overwriting or appending based on current content."""
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return

        if cls.should_overwrite_file(file_path, content_type):
            file_path.write_text(content)
            return

        current_content = file_path.read_text()
        
        # Handle imports merging
        current_imports = {}  # Dictionary to store imports by module path
        current_body = []
        new_imports = {}
        new_body = []
        
        # Split current content into imports and body
        in_imports = True
        for line in current_content.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                if line.startswith(('from ', 'import ')):
                    if line.startswith('from '):
                        module_path = line.split(' import ')[0]
                        imports = [i.strip() for i in line.split(' import ')[1].split(',')]
                        if module_path in current_imports:
                            current_imports[module_path].extend(imports)
                        else:
                            current_imports[module_path] = imports
                    else:
                        current_imports[line] = []
                else:
                    in_imports = False
                    current_body.append(line)
            elif not in_imports:
                current_body.append(line)
                
        # Split new content into imports and body
        in_imports = True
        for line in content.split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                if line.startswith(('from ', 'import ')):
                    if line.startswith('from '):
                        module_path = line.split(' import ')[0]
                        imports = [i.strip() for i in line.split(' import ')[1].split(',')]
                        if module_path in new_imports:
                            new_imports[module_path].extend(imports)
                        else:
                            new_imports[module_path] = imports
                    else:
                        new_imports[line] = []
                else:
                    in_imports = False
                    new_body.append(line)
            elif not in_imports:
                new_body.append(line)

        # Merge imports
        all_imports = {}
        for module_path, imports in current_imports.items():
            if module_path not in all_imports:
                all_imports[module_path] = set(imports)
            else:
                all_imports[module_path].update(imports)
                
        for module_path, imports in new_imports.items():
            if module_path not in all_imports:
                all_imports[module_path] = set(imports)
            else:
                all_imports[module_path].update(imports)

        # Generate final import statements
        import_statements = []
        for module_path, imports in sorted(all_imports.items()):
            if imports:
                import_statements.append(f"{module_path} import {', '.join(sorted(imports))}")
            else:
                import_statements.append(module_path)

        # Combine content
        final_content = '\n'.join(import_statements)
        if final_content and current_body:
            final_content += '\n\n'
        final_content += '\n'.join(current_body)
        if final_content and new_body:
            final_content += '\n\n'
        final_content += '\n'.join(new_body)

        file_path.write_text(final_content)
    

def snake_case(text):
    """
    Convert text to snake_case, handling special cases.
    Examples:
        ProductViewSet -> product_viewset
        TestViewSetWithoutImport -> test_viewset_without_import
        Already_Snake_Case -> already_snake_case
        UserProfile -> user_profile
        ABC -> a_b_c
    """
    # Handle ViewSet special case anywhere in the text
    text = text.replace('ViewSet', 'Viewset')
    
    # If text contains underscores, just convert to lowercase
    if '_' in text:
        return text.lower()
    
    # Special handling for acronyms (sequence of capital letters)
    result = []
    i = 0
    while i < len(text):
        char = text[i]
        # Check for acronym sequence (consecutive uppercase letters)
        if char.isupper() and i + 1 < len(text) and text[i + 1].isupper():
            acronym_end = i + 1
            while acronym_end < len(text) and text[acronym_end].isupper():
                acronym_end += 1
            if i != 0:
                result.append('_')
            result.extend('_'.join(text[i:acronym_end].lower()))
            i = acronym_end
        else:
            # Regular snake_case conversion for camelCase/PascalCase
            if char.isupper() and i != 0:
                result.append('_')
            result.append(char.lower())
            i += 1
    
    # Replace 'viewset' with 'viewset' to ensure consistent casing
    final = ''.join(result).replace('view_set', 'viewset')
    
    return final

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
        tests_py.write_text("""from django.test import TestCase

                            # Create your tests here""")

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


def extract_file_contents(file_path):
    """
    Extracts imports and top-level class definitions from a file.
    Returns a dictionary with 'imports' as one key and each top-level class name as additional keys.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all imports
    import_lines = []
    for line in content.split('\n'):
        if line.strip() and (line.strip().startswith('from ') or line.strip().startswith('import ')):
            import_lines.append(line)

    imports = "\n".join(import_lines)

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

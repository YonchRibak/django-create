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

            # Clean and split content into non-empty lines
            # actual_lines = set(line.strip() for line in content.split('\n') if line.strip())
            # expected_lines = set(line.strip() for line in [expected_import, expected_comment] if line.strip())
            expected_content = '\n'.join([expected_import, expected_comment])

            # Consider it default if actual lines exactly match expected lines
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
    
# def render_template(template_path, **kwargs):
#     """
#     Reads a template file and replaces placeholders with provided values.
#     """
#     with open(template_path, 'r') as file:
#         content = file.read()

#     # Replace placeholders in the content with the provided keyword arguments
#     for key, value in kwargs.items():
#         placeholder = f"{{{{ {key} }}}}"
#         content = content.replace(placeholder, value)

#     return content

# def save_rendered_template(content, output_path):
#     """
#     Saves rendered template content to the specified output path.
#     """
#     with open(output_path, 'w') as file:
#         file.write(content)

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
# def inject_element_into_file(file_path, element_content):
#     """
#     Injects the given element content into an existing file without altering other content.
    
#     Used for adding a new model, view, or serializer to an existing file like models.py.
#     """
#     with open(file_path, 'a') as f:
#         f.write("\n\n" + element_content)

#     click.echo(f"Injected content into '{file_path}'.")

# def create_element_file(element_file_path, element_content):
#     """
#     Create a file with the specified content at the given path, ensuring the directory exists.
#     """
#     # Convert element_file_path to a Path object if it's a string
#     element_file_path = Path(element_file_path)
    
#     # Ensure the parent directory exists
#     element_file_path.parent.mkdir(parents=True, exist_ok=True)
    
#     save_rendered_template(element_content, element_file_path)

# def add_import_to_file(init_file_path, element_name, element_file_name, is_double_dot=False):
#     """
#     Adds an import statement to a specified file (e.g., models/__init__.py) for the new element.
    
#     Can be used to add imports for models, views, serializers, etc.
#     """
#     if is_double_dot:
#         import_statement = f"from ..{element_file_name[:-3]} import {element_name}\n"
#     else: 
#         import_statement = f"from .{element_file_name[:-3]} import {element_name}\n"

#     # Ensure __init__.py exists
#     os.makedirs(os.path.dirname(init_file_path), exist_ok=True)
#     if not os.path.exists(init_file_path):
#         with open(init_file_path, 'w') as f:
#             f.write("# Imports for Django elements\n")

#     # Check if the import already exists
#     with open(init_file_path, 'r') as f:
#         init_content = f.read()

#     if import_statement not in init_content:
#         with open(init_file_path, 'a') as f:
#             f.write(import_statement)
#         click.echo(f"Added import to '{init_file_path}': {import_statement.strip()}")

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

# def is_import_in_file(file, import_txt) -> bool:
#     """
#     Check if necessary import statement is present in file.
#     """
#     with open(file, 'r') as file:
#         content = file.read()
#         return import_txt in content
    

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

# def add_import(file_path, import_statement):
#     """
#     Add an import statement to a Python file if it doesn't exist.
#     Handles both 'from x import y' and 'import x' statements.
#     Merges imports from same module and preserves file formatting.
    
#     Args:
#         file_path: Path to the Python file
#         import_statement: Import statement to add (e.g., "from .models import Model" or "import module")
    
#     Examples:
#         add_import(file_path, "from .models import User")
#         add_import(file_path, "from rest_framework import viewsets")
#         add_import(file_path, "import datetime")
#     """
#     with open(file_path, 'r') as f:
#         content = f.read()
        
#     # If the exact import already exists, do nothing
#     if import_statement in content:
#         return
        
#     # Parse the import statement
#     if import_statement.startswith('from '):
#         # Handle 'from x import y' style imports
#         module = import_statement.split(' import ')[0][5:]
#         imports = import_statement.split(' import ')[1].strip()
#     else:
#         # Handle 'import x' style imports
#         module = import_statement[7:]  # len('import ') = 7
#         imports = None

#     # Find all existing imports
#     import_pattern = r'^(?:from|import) .+$'
#     matches = list(re.finditer(import_pattern, content, re.MULTILINE))
    
#     if matches:
#         last_import_end = matches[-1].end()
        
#         if imports:  # 'from x import y' style
#             # Check if we already have imports from this module
#             module_pattern = fr'from {re.escape(module)} import ([^\n]+)'
#             existing_import = re.search(module_pattern, content)
            
#             if existing_import:
#                 # Get existing imports and add new ones
#                 existing_imports = [x.strip() for x in existing_import.group(1).split(',')]
#                 new_imports = [x.strip() for x in imports.split(',')]
                
#                 # Combine imports, remove duplicates, and sort
#                 combined_imports = sorted(set(existing_imports + new_imports))
                
#                 # Replace the existing import line
#                 new_import_line = f"from {module} import {', '.join(combined_imports)}"
#                 new_content = (
#                     content[:existing_import.start()] +
#                     new_import_line +
#                     content[existing_import.end():]
#                 )
#             else:
#                 # Add new import line after the last import
#                 new_content = (
#                     content[:last_import_end] +
#                     f"\n{import_statement}" +
#                     content[last_import_end:]
#                 )
#         else:  # 'import x' style
#             # Add new import line after the last import
#             new_content = (
#                 content[:last_import_end] +
#                 f"\n{import_statement}" +
#                 content[last_import_end:]
#             )
#     else:
#         # No imports found, add at the beginning of the file
#         new_content = f"{import_statement}\n\n{content}"

#     # Write the modified content back to the file
#     with open(file_path, 'w') as f:
#         f.write(new_content)

# def merge_item_into_import(existing_import_line, item, from_statement):
#     """
#     Merge an item into an existing import line if the from_statement matches.
    
#     Args:
#         existing_import_line (str): The existing import line.
#         item (str): The item to be merged into the import line.
#         from_statement (str): The from statement to check against the existing import line.
    
#     Returns:
#         str: The updated import line with the item merged in.
#     """
#     if existing_import_line.startswith(from_statement):
#         # Extract the existing imports
#         existing_imports = existing_import_line.split('import ')[-1].split(', ')
        
#         # Check if the item is already in the existing imports
#         if item in existing_imports:
#             return existing_import_line
        
#         # Merge the item into the existing imports
#         existing_imports.append(item)
#         existing_imports = sorted(set(existing_imports))
        
#         # Construct the updated import line
#         return f"{from_statement} import {', '.join(existing_imports)}"
    
#     # If the from_statement doesn't match, return the original import line
#     return existing_import_line

# def modify_import_statement_to_double_dot(import_line):
#     """
#     Modify an import statement to use double-dot (..) instead of single-dot (.).
#     If the import statement already uses double-dot, it is left as-is.
    
#     Args:
#         import_line (str): The import statement to be modified.
        
#     Returns:
#         str: The modified import statement using double-dot, or the original line if it already uses double-dot.
#     """
#     if import_line.startswith("from .."):
#         return import_line
#     elif import_line.startswith("from .") and not import_line.startswith("from .."):
#         return f"from ..{import_line[6:]}"
#     elif import_line.startswith("import "):
#         return import_line
#     else:
#         return import_line
    
# def create_correct_import_statement(current_file_path, item_to_import_name, item_to_import_path):
#     """
#     Create the correct relative import statement based on file locations.
#     Works with both existing and future file paths.
    
#     Args:
#         current_file_path: Path to the current/future file needing the import
#         item_to_import_name: Name of the item to import (e.g., 'UserModel', 'UserView')
#         item_to_import_path: Full path to the file containing/will contain the item
        
#     Returns:
#         str: Properly formatted import statement
#     """
#     # Convert paths to Path objects
#     current = Path(current_file_path).resolve()
#     target = Path(item_to_import_path).resolve()
    
#     # Get parents as a list for both paths
#     current_parts = current.parent.parts
#     target_parts = target.parent.parts
    
#     # Find common prefix
#     common_prefix_len = 0
#     for c, t in zip(current_parts, target_parts):
#         if c != t:
#             break
#         common_prefix_len += 1
    
#     # Calculate dots needed (how many levels to go up)
#     dots = len(current_parts) - common_prefix_len
    
#     # Get the import path parts (after going up)
#     import_path_parts = target_parts[common_prefix_len:]
    
#     # If we're in the same directory
#     if dots == 0 and not import_path_parts:
#         return f"from .{target.stem} import {item_to_import_name}"
    
#     # If we need to go up and/or across
#     prefix = '.' * (dots + 1)  # +1 because we always need at least one dot
#     suffix = '.'.join(import_path_parts + (target.stem,))
    
#     return f"from {prefix}{suffix} import {item_to_import_name}"

# def process_imports(imports_string, source_file_path):
#     """
#     Process import statements, adjusting relative imports while preserving format.
    
#     Args:
#         imports_string: String containing import statements
#         source_file_path: Path to the file that will contain these imports
        
#     Returns:
#         str: Processed import statements with correct relative paths
#     """
#     if not imports_string:
#         return ""
        
#     # Split but preserve all newlines
#     import_lines = imports_string.split('\n')
#     processed_lines = []
    
#     i = 0
#     while i < len(import_lines):
#         line = import_lines[i]
        
#         # Preserve empty lines exactly
#         if not line.strip():
#             processed_lines.append(line)
#             i += 1
#             continue
            
#         # Preserve comments exactly
#         if line.strip().startswith('#'):
#             processed_lines.append(line)
#             i += 1
#             continue
            
#         # Check if this is a multiline import
#         if '(' in line and ')' not in line:
#             # Collect all lines until we find the closing parenthesis
#             full_import = [line]
#             i += 1
#             while i < len(import_lines) and ')' not in import_lines[i]:
#                 full_import.append(import_lines[i])
#                 i += 1
#             if i < len(import_lines):  # Add the line with closing parenthesis
#                 full_import.append(import_lines[i])
            
#             # Process the multiline import
#             if line.strip().startswith('from .'):
#                 try:
#                     module_path = line.split(' import ')[0].replace('from .', '').replace('from ..', '')
#                     target_file = Path(source_file_path).parent / f"{module_path}.py"
#                     new_base = create_correct_import_statement(
#                         str(source_file_path),
#                         "placeholder",
#                         str(target_file)
#                     ).replace("import placeholder", "import (")
#                     processed_lines.extend([new_base] + full_import[1:])
#                 except Exception:
#                     processed_lines.extend(full_import)
#             else:
#                 processed_lines.extend(full_import)
#             i += 1
#             continue
            
#         # Single line import
#         if line.strip().startswith('from .'):
#             try:
#                 parts = line.strip().split(' import ')
#                 if len(parts) == 2:
#                     module_path = parts[0].replace('from .', '').replace('from ..', '')
#                     items = parts[1].strip()
                    
#                     target_file = Path(source_file_path).parent / f"{module_path}.py"
#                     new_import = create_correct_import_statement(
#                         str(source_file_path),
#                         "placeholder",
#                         str(target_file)
#                     )
#                     processed_lines.append(
#                         new_import.replace("import placeholder", f"import {items}")
#                     )
#                 else:
#                     processed_lines.append(' '.join(line.split()))
#             except Exception:
#                 processed_lines.append(' '.join(line.split()))
#         else:
#             # Regular import - just normalize whitespace
#             processed_lines.append(' '.join(line.split()))
#         i += 1
            
#     return '\n'.join(processed_lines)

# def determine_import_path(app_path, module_type, is_folderizing=False):
#     """
#     Determine the correct import path style based on app structure and command context.
#     Always prefer folder-level imports from sibling folders.
    
#     Args:
#         app_path (Path): Path to the Django app
#         module_type (str): Type of module ('models', 'serializers', 'viewsets', etc.)
#         is_folderizing (bool): Whether this is being called during folderize command
    
#     Returns:
#         tuple: (import_style, has_folder)
#             import_style: 'dot' for relative import (.models), 
#                          'dotdot' for parent relative import (..models),
#                          'direct' for direct import (models)
#             has_folder: Whether the module folder exists or will exist
#     """
#     if not module_type:
#         return "direct", False

#     # During folderize or for imports between folders, always use dotdot style
#     if is_folderizing or module_type in ['models', 'serializers', 'viewsets', 'views']:
#         return "dotdot", True

#     # For other cases (e.g., Django imports), use direct style
#     return "direct", False

# def format_import_statement(module_type, items, import_style='dot'):
#     """
#     Format an import statement based on the determined style.
#     Always formats as package-level imports for internal modules.
    
#     Args:
#         module_type (str): The module to import from ('models', 'serializers', etc.)
#         items (str or list): Item(s) to import
#         import_style (str): 'dot', 'dotdot', or 'direct'
    
#     Returns:
#         str: Formatted import statement
#     """
#     if items is None:
#         items = ['None']
#     elif isinstance(items, str):
#         items = [items]
        
#     items_str = ', '.join(items)
    
#     # If it's one of our module types, always import from the package
#     if module_type in ['models', 'serializers', 'viewsets', 'views']:
#         return f"from ..{module_type} import {items_str}"
    
#     # For empty module type with dot/dotdot style
#     if not module_type:
#         if import_style == "dot":
#             return f"from . import {items_str}"
#         elif import_style == "dotdot":
#             return f"from .. import {items_str}"
        
#     # For other imports (Django, etc.), use direct import
#     return f"from {module_type} import {items_str}"

# def update_template_imports(template_content, app_path, is_folderizing=False):
#     """
#     Update import statements in a template based on app structure.
#     Ensures all internal module imports are package-level.
    
#     Args:
#         template_content (str): The template content to update
#         app_path (Path): Path to the Django app
#         is_folderizing (bool): Whether this is being called during folderize
    
#     Returns:
#         str: Updated template content
#     """

#     if template_content is None:
#         return None

#     if not template_content.strip():
#         return template_content

#     # Simplified pattern that matches both direct and nested imports
#     base_pattern = r'from \.{1,2}(models|serializers|views|viewsets)(?:\.[a-zA-Z0-9_.]+)? import ([^#\n]+)(#.*)?$'
    
#     # Split content into lines to preserve comments and formatting
#     lines = template_content.split('\n')
#     processed_lines = []

#     for line in lines:
#         match = re.match(base_pattern, line.strip())
#         if match:
#             module_type = match.group(1)  # The module type (models, serializers, etc.)
#             imports = match.group(2)  # The imported items
#             comment = match.group(3) or ''  # Any inline comment
            
#             # Preserve the space before the comment if it exists
#             if comment and not comment.startswith(' '):
#                 comment = ' ' + comment
            
#             # Clean up the imports
#             items = [item.strip() for item in imports.split(',')]
            
#             # Determine import style based on module type and context
#             import_style, _ = determine_import_path(app_path, module_type, is_folderizing)
            
#             # Format the import statement using the determined style
#             new_import = format_import_statement(module_type, items, import_style)
            
#             # Add back any comments
#             if comment:
#                 new_import += comment
                
#             processed_lines.append(new_import)
#         else:
#             processed_lines.append(line)

#     return '\n'.join(processed_lines)
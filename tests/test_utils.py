import pytest
import os
from pathlib import Path
from django_create.utils import (
    Utils,
    create_mock_django_app,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    snake_case,
    extract_file_contents,
    add_import,
    merge_item_into_import, 
    modify_import_statement_to_double_dot,
    create_correct_import_statement, 
    process_imports
)

def test_create_mock_django_app(tmp_path):
    # Create a mock Django app with all options enabled
    app_path = create_mock_django_app(
        tmp_path, 
        app_name='testapp',
        with_models_file=True, 
        with_models_folder=True, 
        with_views_folder=True, 
        with_viewsets_folder=True, 
        with_serializers_folder=True, 
        with_tests_folder=True
    )

    # Check that the app directory was created
    assert app_path.exists()
    assert app_path.is_dir()

    # Check for models.py
    models_py_path = app_path / 'models.py'
    assert models_py_path.exists()
    assert models_py_path.is_file()
    assert models_py_path.read_text() == "# models.py file for testing\n"

    # Check for models folder and __init__.py
    models_folder_path = app_path / 'models'
    models_init_path = models_folder_path / '__init__.py'
    assert models_folder_path.exists()
    assert models_folder_path.is_dir()
    assert models_init_path.exists()
    assert models_init_path.read_text() == "# models/__init__.py for testing\n"

    # Check for views folder and __init__.py
    views_folder_path = app_path / 'views'
    views_init_path = views_folder_path / '__init__.py'
    assert views_folder_path.exists()
    assert views_folder_path.is_dir()
    assert views_init_path.exists()
    assert views_init_path.read_text() == "# views/__init__.py for testing\n"

    # Check for viewsets folder and __init__.py
    viewsets_folder_path = app_path / 'viewsets'
    viewsets_init_path = viewsets_folder_path / '__init__.py'
    assert viewsets_folder_path.exists()
    assert viewsets_folder_path.is_dir()
    assert viewsets_init_path.exists()
    assert viewsets_init_path.read_text() == "# viewsets/__init__.py for testing\n"

    # Check for serializers folder and __init__.py
    serializers_folder_path = app_path / 'serializers'
    serializers_init_path = serializers_folder_path / '__init__.py'
    assert serializers_folder_path.exists()
    assert serializers_folder_path.is_dir()
    assert serializers_init_path.exists()
    assert serializers_init_path.read_text() == "# serializers/__init__.py for testing\n"

    # Check for tests folder and __init__.py
    tests_folder_path = app_path / 'tests'
    tests_init_path = tests_folder_path / '__init__.py'
    test_sample_path = tests_folder_path / 'test_sample.py'
    assert tests_folder_path.exists()
    assert tests_folder_path.is_dir()
    assert tests_init_path.exists()
    assert tests_init_path.read_text() == "# tests/__init__.py for testing\n"
    assert test_sample_path.exists()
    assert test_sample_path.read_text() == "# Sample test file for testing\n"
    
def test_inject_element_into_file(tmp_path):
    # Create a mock Django app with models.py
    app_path = create_mock_django_app(tmp_path, with_models_file=True)
    models_py_path = app_path / 'models.py'
    
    # Define the element content to inject
    element_content = "class NewModel(models.Model):\n    pass"
    
    # Inject the content into models.py
    inject_element_into_file(str(models_py_path), element_content)
    
    # Verify that the content was added correctly
    expected_content = "# models.py file for testing\n\n\nclass NewModel(models.Model):\n    pass"
    assert models_py_path.read_text() == expected_content

def test_create_element_file(tmp_path):
    # Create a mock Django app with a models folder
    app_path = create_mock_django_app(tmp_path, with_models_folder=True)
    models_folder_path = app_path / 'models'
    model_file_path = models_folder_path / 'new_model.py'
    
    # Define the element content for a model
    element_content = "class NewModel(models.Model):\n    pass"
    
    # Create a new model file inside the models folder
    create_element_file(str(model_file_path), element_content)
    
    # Verify that the new model file was created correctly
    assert model_file_path.exists()
    assert model_file_path.read_text() == element_content

def test_add_import_to_file(tmp_path):
    # Create a mock Django app with a models folder and __init__.py
    app_path = create_mock_django_app(tmp_path, with_models_folder=True)
    init_file_path = app_path / 'models' / '__init__.py'
    element_name = "NewModel"
    element_file_name = "new_model.py"

    # Add the import statement to __init__.py
    add_import_to_file(str(init_file_path), element_name, element_file_name)
    
    # Verify that the import statement was added correctly
    expected_import = "from .new_model import NewModel\n"
    assert expected_import in init_file_path.read_text()

    # Ensure that the import statement is not duplicated if added again
    add_import_to_file(str(init_file_path), element_name, element_file_name)
    assert init_file_path.read_text().count(expected_import) == 1

def test_snake_case():
    # Test snake_case function for various cases
    assert snake_case('CamelCase') == 'camel_case'
    assert snake_case('CamelCASE') == 'camel_case'
    assert snake_case('camelCase') == 'camel_case'
    assert snake_case('Already_Snake_Case') == 'already_snake_case'

def test_extract_file_contents_with_imports_and_single_class(tmp_path):
    # Create a sample file with imports and a single top-level class
    file_path = tmp_path / "sample.py"
    file_content = """
import os
from django.db import models

class SampleModel(models.Model):
    name = models.CharField(max_length=100)
"""
    file_path.write_text(file_content)

    # Extract content using extract_file_contents
    result = extract_file_contents(file_path)

    # Assertions
    assert "imports" in result
    assert result["imports"] == "import os\nfrom django.db import models"
    assert "SampleModel" in result
    assert "class SampleModel(models.Model):" in result["SampleModel"]
    assert "name = models.CharField(max_length=100)" in result["SampleModel"]


def test_extract_file_contents_with_multiple_classes(tmp_path):
    # Create a sample file with multiple top-level classes
    file_path = tmp_path / "sample.py"
    file_content = """
from django.db import models
from ..utils import some_function 

class SampleModel(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

class AnotherModel(models.Model):
    description = models.TextField()
"""
    file_path.write_text(file_content)

    # Extract content using extract_file_contents
    result = extract_file_contents(file_path)

    # Assertions
    assert "imports" in result
    assert "from django.db import models" in result["imports"]
    assert "from ..utils import some_function" in result["imports"]
    assert "SampleModel" in result
    assert "class SampleModel(models.Model):" in result["SampleModel"]
    assert "AnotherModel" in result
    assert "class AnotherModel(models.Model):" in result["AnotherModel"]


def test_extract_file_contents_with_nested_classes(tmp_path):
    # Create a sample file with a top-level class containing a nested class
    file_path = tmp_path / "sample.py"
    file_content = """
from django.db import models

class OuterClass:
    class NestedClass:
        pass

class TopLevelModel(models.Model):
    name = models.CharField(max_length=100)
"""
    file_path.write_text(file_content)

    # Extract content using extract_file_contents
    result = extract_file_contents(file_path)

    # Assertions: Only top-level classes should be captured
    assert "imports" in result
    assert result["imports"] == "from django.db import models"
    assert "OuterClass" in result
    assert "class OuterClass:" in result["OuterClass"]
    assert "class NestedClass:" in result["OuterClass"]
    assert "TopLevelModel" in result
    assert "class TopLevelModel(models.Model):" in result["TopLevelModel"]
    assert "name = models.CharField(max_length=100)" in result["TopLevelModel"]
    assert "NestedClass" not in result  # Nested classes should not appear at the top level


def test_extract_file_contents_with_no_imports_or_classes(tmp_path):
    # Create a file with no imports or classes
    file_path = tmp_path / "sample.py"
    file_content = """
# This is a comment
x = 5
"""
    file_path.write_text(file_content)

    # Extract content using extract_file_contents
    result = extract_file_contents(file_path)

    # Assertions
    assert "imports" in result
    assert result["imports"] == ""
    assert len(result) == 1  # Only 'imports' should be present

def test_extract_file_contents_multiple_imports(tmp_path):
    """Test that extract_file_contents correctly extracts multiple import lines."""
    # Create a test file with multiple imports
    test_file = tmp_path / "test_module.py"
    test_content = """
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class SampleTest(TestCase):
    def test_something(self):
        self.client = APIClient()
        self.assertTrue(True)
"""
    test_file.write_text(test_content)

    # Extract content
    result = extract_file_contents(test_file)

    # Expected imports
    expected_imports = (
        "from django.test import TestCase\n"
        "from django.urls import reverse\n"
        "from rest_framework import status\n"
        "from rest_framework.test import APIClient"
    )

    # Print debug info
    print("\nExtracted imports:")
    print(result["imports"])
    print("\nExpected imports:")
    print(expected_imports)

    # Verify imports
    assert result["imports"] == expected_imports, "Multiple import lines not correctly extracted"

    # Verify class content is still correct
    assert "SampleTest" in result
    assert "def test_something" in result["SampleTest"]

def test_add_import(tmp_path):
    """Test the add_import function with various scenarios."""
    # Create a test file
    test_file = tmp_path / "test_file.py"
    initial_content = """from rest_framework import serializers
from .models import User
from django.db import models

class SampleSerializer(serializers.ModelSerializer):
    pass
"""
    test_file.write_text(initial_content)

    # Test cases
    add_import(test_file, "from .models import Profile")  # Should merge with existing .models import
    add_import(test_file, "from datetime import datetime")  # Should add new import
    add_import(test_file, "import os")  # Should add simple import
    add_import(test_file, "from .models import User")  # Should not duplicate
    add_import(test_file, "from rest_framework import viewsets")  # Should add to existing rest_framework import

    content = test_file.read_text()
    print("\nResulting content:")
    print(content)

    # Verify imports
    assert "from .models import Profile, User" in content
    assert "from datetime import datetime" in content
    assert "import os" in content
    assert "from rest_framework import serializers, viewsets" in content
    assert content.count("from .models import") == 1  # No duplicate imports
    assert content.count("User") == 1  # No duplicate model imports


def test_merge_item_into_import_existing_item():
    existing_import_line = "from ..models import User, Product"
    item = "User"
    from_statement = "from ..models import"
    
    updated_import_line = merge_item_into_import(existing_import_line, item, from_statement)
    assert updated_import_line == "from ..models import User, Product"

def test_merge_item_into_import_different_from_statement():
    existing_import_line = "from ..serializers import UserSerializer, ProductSerializer"
    item = "OrderSerializer"
    from_statement = "from ..models import"
    
    updated_import_line = merge_item_into_import(existing_import_line, item, from_statement)
    assert updated_import_line == "from ..serializers import UserSerializer, ProductSerializer"

def test_modify_import_statement_to_double_dot():
    # Test cases
    test_cases = [
        ("from .models import Product, User, SomeOtherModel", "from ..models import Product, User, SomeOtherModel"),
        ("from ..models import Product, User, SomeOtherModel", "from ..models import Product, User, SomeOtherModel"),
        ("import datetime", "import datetime"),
        ("from models import Product", "from models import Product"),
    ]

    for input_line, expected_output in test_cases:
        if isinstance(expected_output, type) and issubclass(expected_output, Exception):
            with expected_output:
                output = modify_import_statement_to_double_dot(input_line)
        else:
            output = modify_import_statement_to_double_dot(input_line)
            assert output == expected_output

def test_create_correct_import_statement(tmp_path):
    """Test the create_correct_import_statement function with various file structures."""
    
    # Create a mock Django app with a specific structure
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_folder=True,
        with_views_folder=True,
        with_serializers_folder=True
    )
    
    # Define paths (don't need to create actual files)
    model_file = app_path / 'models' / 'user.py'
    view_file = app_path / 'views' / 'user.py'
    nested_view_file = app_path / 'views' / 'api' / 'user.py'
    serializer_file = app_path / 'serializers' / 'user.py'
    
    # Test cases
    test_cases = [
        # Format: current_file, target_file, item_name, expected_import
        
        # From view to model (up one, into models)
        (
            str(view_file),
            str(model_file),
            "UserModel",
            "from ..models.user import UserModel"
        ),
        
        # From nested view to model (up two, into models)
        (
            str(nested_view_file),
            str(model_file),
            "UserModel",
            "from ...models.user import UserModel"
        ),
        
        # From model to view (up one, into views)
        (
            str(model_file),
            str(view_file),
            "UserView",
            "from ..views.user import UserView"
        ),
        
        # From model to nested view (up one, into views/api)
        (
            str(model_file),
            str(nested_view_file),
            "UserApiView",
            "from ..views.api.user import UserApiView"
        ),
        
        # From serializer to model (up one, into models)
        (
            str(serializer_file),
            str(model_file),
            "UserModel",
            "from ..models.user import UserModel"
        ),
        
        # Same directory import
        (
            str(app_path / 'models' / 'product.py'),
            str(app_path / 'models' / 'user.py'),
            "UserModel",
            "from .user import UserModel"
        ),
        
        # Import from future nested path
        (
            str(app_path / 'models' / 'deep' / 'nested' / 'item.py'),
            str(app_path / 'models' / 'user.py'),
            "UserModel",
            "from ...user import UserModel"
        ),
        
        # Import to future nested path
        (
            str(app_path / 'models' / 'user.py'),
            str(app_path / 'models' / 'deep' / 'nested' / 'item.py'),
            "ItemModel",
            "from .deep.nested.item import ItemModel"
        )
    ]
    
    # Run the tests without creating the files
    for current_file, target_file, item_name, expected in test_cases:
        result = create_correct_import_statement(current_file, item_name, target_file)
        
        # Assert the result
        assert result == expected, \
            f"Failed: from {current_file} importing {item_name} from {target_file}.\n" \
            f"Expected: {expected}\nGot: {result}"

def test_create_correct_import_statement_different_directories(tmp_path):
    """Test create_correct_import_statement with very different directory structures."""
    
    # Test with paths in completely different directories
    path1 = tmp_path / "dir1" / "file1.py"
    path2 = tmp_path / "dir2" / "subdir" / "file2.py"
    
    result = create_correct_import_statement(str(path1), "MyClass", str(path2))
    expected = "from ..dir2.subdir.file2 import MyClass"
    
    assert result == expected, \
        f"Failed to create correct import for different directories.\n" \
        f"Expected: {expected}\nGot: {result}"
def test_create_correct_import_statement_special_cases(tmp_path):
    """Test special cases for create_correct_import_statement function."""
    
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_folder=True
    )
    
    test_cases = [
        # Empty directories between files
        (
            str(app_path / 'models' / 'empty1' / 'empty2' / 'model.py'),
            str(app_path / 'models' / 'user.py'),
            "UserModel",
            "from ...user import UserModel"
        ),
        
        # Very deep nesting
        (
            str(app_path / 'models' / 'a' / 'b' / 'c' / 'd' / 'deep.py'),
            str(app_path / 'models' / 'user.py'),
            "UserModel",
            "from .....user import UserModel"
        ),
        
        # Importing from parent to deeply nested
        (
            str(app_path / 'models' / 'parent.py'),
            str(app_path / 'models' / 'a' / 'b' / 'c' / 'child.py'),
            "ChildModel",
            "from .a.b.c.child import ChildModel"
        ),
    ]
    
    for current_file, target_file, item_name, expected in test_cases:
        result = create_correct_import_statement(current_file, item_name, target_file)
        assert result == expected, \
            f"Failed: from {current_file} importing {item_name} from {target_file}.\n" \
            f"Expected: {expected}\nGot: {result}"
        
def test_process_imports(tmp_path):
    """Test the process_imports function with various import scenarios."""
    
    # Create a base structure for testing
    test_dir = tmp_path / "testproject" / "testapp"
    test_dir.mkdir(parents=True)
    
    model_file = test_dir / "models.py"
    view_file = test_dir / "views.py"
    nested_view_file = test_dir / "views" / "nested" / "view.py"
    
    nested_view_file.parent.mkdir(parents=True)
    
    # Expected multiline format with proper indentation
    multiline_expected = "from .views import (\n    MyView,\n    OtherView\n)"
    
    test_cases = [
        # ... (previous test cases remain the same until multiline case)
        
        # Multiline imports - match exact format
        (
            model_file,
            "from .views import (\n    MyView,\n    OtherView\n)",
            multiline_expected
        ),
    ]
    
    for source_file, imports_string, expected in test_cases:
        result = process_imports(imports_string, source_file)
        assert result == expected, (
            f"Failed processing imports for {source_file.name}\n"
            f"Input:\n{imports_string}\n"
            f"Expected:\n{expected}\n"
            f"Got:\n{result}"
        )

def test_process_imports_invalid_cases(tmp_path):
    """Test process_imports with invalid or malformed imports."""
    
    test_file = tmp_path / "test.py"
    
    test_cases = [
        # Malformed import statement - preserve it
        (
            "from . import",
            "from . import"
        ),
        
        # Invalid relative import
        (
            "from .nonexistent import Something",
            "from .nonexistent import Something"
        ),
        
        # Empty lines only - preserve exactly
        (
            "\n\n\n",
            "\n\n\n"
        ),
        
        # Comments only
        (
            "# just a comment\n# another comment",
            "# just a comment\n# another comment"
        ),
    ]
    
    for imports_string, expected in test_cases:
        result = process_imports(imports_string, test_file)
        assert result == expected, (
            f"Failed processing invalid import case\n"
            f"Input:\n{imports_string}\n"
            f"Expected:\n{expected}\n"
            f"Got:\n{result}"
        )
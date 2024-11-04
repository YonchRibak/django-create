import pytest
from pathlib import Path
from django_create.utils import Utils, snake_case, create_mock_django_app, extract_file_contents

def test_is_default_content(tmp_path):
    """Test Utils.is_default_content with various file contents."""
    test_file = tmp_path / "test.py"
    
    # Test cases with expected results
    test_cases = [
        # Default models.py content
        (
            'models',
            "from django.db import models\n\n# Create your models here",
            True
        ),
        # Default content with different whitespace
        (
            'models',
            "from django.db import models\n\n\n# Create your models here\n",
            True
        ),
        # Non-default content
        (
            'models',
            "from django.db import models\nclass TestModel(models.Model):\n    pass",
            False
        ),
        # Empty file
        (
            'models',
            "",
            False
        ),
        # Default content for views
        (
            'views',
            "from django.views import View\n\n# Create your views here",
            True
        )
    ]
    
    for file_type, content, expected in test_cases:
        test_file.write_text(content)
        result = Utils.is_default_content(test_file, file_type)
        assert result == expected, f"Failed for {file_type} with content: {content}"

def test_determine_import_style(tmp_path):
    """Test Utils.determine_import_style with different app structures."""
    app_path = create_mock_django_app(tmp_path, 'testapp')
    
    # Create some module folders
    (app_path / 'models').mkdir(exist_ok=True)
    (app_path / 'views').mkdir(exist_ok=True)
    
    # Test cases
    assert Utils.determine_import_style(app_path, 'models') == 'dotdot'
    assert Utils.determine_import_style(app_path, 'views') == 'dotdot'
    assert Utils.determine_import_style(app_path, 'serializers') == 'dot'  # No folder
    assert Utils.determine_import_style(app_path, None) == 'dot'  # Invalid module type

def test_process_template_imports(tmp_path):
    """Test Utils.process_template_imports with different app structures."""
    app_path = create_mock_django_app(tmp_path, 'testapp')
    
    # Create models folder to test import style switching
    (app_path / 'models').mkdir(exist_ok=True)
    
    test_cases = [
        # Content with imports to modify
        (
            "from .models import Model\nfrom .views import View",
            "from ..models import Model\nfrom .views import View"  # models folder exists
        ),
        # Content with no imports
        (
            "class TestClass:\n    pass",
            "class TestClass:\n    pass"
        ),
        # Mixed import styles
        (
            "from ..models import Model\nfrom .views import View",
            "from ..models import Model\nfrom .views import View"
        )
    ]
    
    for content, expected in test_cases:
        result = Utils.process_template_imports(content, app_path)
        assert result == expected

def test_render_template(tmp_path):
    """Test Utils.render_template with various template contents."""
    app_path = create_mock_django_app(tmp_path, 'testapp')
    template_path = tmp_path / 'template.txt'
    
    # Create models folder to test import modifications
    (app_path / 'models').mkdir(exist_ok=True)
    
    test_cases = [
        # Template with variables and imports
        (
            "from .models import {{ model_name }}\nclass {{ class_name }}:\n    pass",
            {'model_name': 'TestModel', 'class_name': 'TestClass'},
            "from ..models import TestModel\nclass TestClass:\n    pass"
        ),
        # Template with only variables
        (
            "class {{ class_name }}:\n    value = {{ value }}",
            {'class_name': 'TestClass', 'value': '42'},
            "class TestClass:\n    value = 42"
        )
    ]
    
    for template_content, variables, expected in test_cases:
        template_path.write_text(template_content)
        result = Utils.render_template(template_path, app_path, **variables)
        assert result == expected

def test_should_overwrite_file(tmp_path):
    """Test Utils.should_overwrite_file with different file states."""
    test_file = tmp_path / "test.py"
    
    # Test non-existent file
    assert Utils.should_overwrite_file(test_file, 'models') == True
    
    # Test file with default content
    test_file.write_text(f"{Utils.DJANGO_IMPORTS['models']}\n\n{Utils.DEFAULT_COMMENTS['models']}")
    assert Utils.should_overwrite_file(test_file, 'models') == True
    
    # Test file with non-default content
    test_file.write_text("class TestModel(models.Model):\n    pass")
    assert Utils.should_overwrite_file(test_file, 'models') == False

def test_write_or_append_content(tmp_path):
    """Test Utils.write_or_append_content with different scenarios."""
    test_file = tmp_path / "test.py"
    new_content = "class NewModel(models.Model):\n    pass"
    
    # Test writing to new file
    Utils.write_or_append_content(test_file, new_content, 'models')
    assert test_file.read_text() == new_content
    
    # Test appending to existing non-default file
    existing_content = "class ExistingModel(models.Model):\n    pass"
    test_file.write_text(existing_content)
    Utils.write_or_append_content(test_file, new_content, 'models')
    assert existing_content in test_file.read_text()
    assert new_content in test_file.read_text()
    
    # Test overwriting file with default content
    default_content = f"{Utils.DJANGO_IMPORTS['models']}\n\n{Utils.DEFAULT_COMMENTS['models']}"
    test_file.write_text(default_content)
    Utils.write_or_append_content(test_file, new_content, 'models')
    assert test_file.read_text() == new_content

def test_snake_case():
    """Test snake_case function with various input formats."""
    test_cases = [
        ('CamelCase', 'camel_case'),
        ('camelCase', 'camel_case'),
        ('ThisIsATest', 'this_is_a_test'),
        ('already_snake_case', 'already_snake_case'),
        ('ABC', 'a_b_c'),
        ('ProductViewSet', 'product_viewset'),
        ('UserProfile', 'user_profile'),
        ('TestViewSetWithoutImport', 'test_viewset_without_import')
    ]
    
    for input_text, expected in test_cases:
        assert snake_case(input_text) == expected

def test_extract_file_contents(tmp_path):
    """Test extract_file_contents with various file contents."""
    test_file = tmp_path / "test.py"
    
    # Test case 1: File with imports and multiple classes
    content = """
from django.db import models
import datetime

class FirstModel(models.Model):
    name = models.CharField(max_length=100)
    
class SecondModel(models.Model):
    date = models.DateTimeField()
    """
    test_file.write_text(content)
    result = extract_file_contents(test_file)
    
    assert "imports" in result
    assert "from django.db import models" in result["imports"]
    assert "import datetime" in result["imports"]
    assert "FirstModel" in result
    assert "SecondModel" in result
    
    # Test case 2: File with nested classes
    content = """
class OuterClass:
    class NestedClass:
        pass
        
class TopLevel:
    pass
    """
    test_file.write_text(content)
    result = extract_file_contents(test_file)
    
    assert "imports" in result
    assert "OuterClass" in result
    assert "TopLevel" in result
    assert "NestedClass" not in result  # Should not extract nested classes

def test_create_mock_django_app(tmp_path):
    """Test create_mock_django_app with various configurations."""
    
    # Test case 1: Create app with all options enabled
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
    
    assert app_path.exists()
    assert (app_path / 'models.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'viewsets').is_dir()
    assert (app_path / 'serializers').is_dir()
    assert (app_path / 'tests').is_dir()
    
    # Test case 2: Create app in subdirectory
    subdir_app = create_mock_django_app(
        tmp_path,
        app_name='subapp',
        subdirectory='subdir',
        with_models_file=True
    )
    
    assert subdir_app.exists()
    assert subdir_app.parent.name == 'subdir'
    assert (subdir_app / 'models.py').exists()
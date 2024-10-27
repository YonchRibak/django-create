import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.utils import create_mock_django_app, snake_case
from django_create.cli import cli  # Import the main CLI entry point
from django_create.commands import folderize

def test_inject_into_models_py(tmp_path):
    # Create a mock Django app with models.py
    app_path = create_mock_django_app(
        tmp_path, 
        app_name='testapp',
        with_models_file=True, 
        with_models_folder=False
    )

    # Define the path to models.py using Pathlib
    models_py_path = app_path / 'models.py'
    runner = CliRunner()
    model_name = "ProductCustomFields"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_model command
    result = runner.invoke(cli, ['testapp', 'create', 'model', model_name])

    # Print output for debugging
    print(result.output)
    print(f"Resolved models.py path: {models_py_path}")
    print(f"models.py exists: {models_py_path.exists()}")

    # Verify that the model was injected into models.py
    assert result.exit_code == 0
    assert f"class {model_name}(models.Model):" in models_py_path.read_text()


def test_create_in_models_folder(tmp_path):
    # Create a mock Django app with a models folder
    app_path = create_mock_django_app(
        tmp_path, 
        app_name='testapp',
        with_models_file=False, 
        with_models_folder=True
    )

    # Define the paths using Pathlib
    models_folder_path = app_path / 'models'
    model_file_name = "product_custom_fields.py"
    model_file_path = models_folder_path / model_file_name
    init_file_path = models_folder_path / '__init__.py'
    runner = CliRunner()
    model_name = "ProductCustomFields"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_model command
    result = runner.invoke(cli, ['testapp', 'create', 'model', model_name])

    # Print output for debugging
    print(result.output)
    print(f"Model file path: {model_file_path}")
    print(f"Model file exists: {model_file_path.exists()}")

    # Verify that the model was created inside the models folder
    assert result.exit_code == 0
    assert model_file_path.exists()
    assert f"class {model_name}(models.Model):" in model_file_path.read_text()
    assert f"from .{model_file_name[:-3]} import {model_name}" in init_file_path.read_text()


def test_create_in_custom_path(tmp_path):
    # Create a mock Django app with a models folder
    app_path = create_mock_django_app(
        tmp_path, 
        app_name='testapp',
        with_models_file=False, 
        with_models_folder=True
    )

    # Define the custom path
    custom_path = 'products/some_other_folder'
    custom_model_folder_path = app_path / 'models' / custom_path
    model_file_name = "product_custom_fields.py"
    model_file_path = custom_model_folder_path / model_file_name
    init_file_path = custom_model_folder_path / '__init__.py'
    runner = CliRunner()
    model_name = "ProductCustomFields"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_model command with --path
    result = runner.invoke(cli, ['testapp', 'create', 'model', model_name, '--path', custom_path])

    # Print output for debugging
    print(result.output)
    print(f"Model file path: {model_file_path}")
    print(f"Model file exists: {model_file_path.exists()}")

    # Verify that the model was created in the custom path
    assert result.exit_code == 0
    assert model_file_path.exists()
    assert f"class {model_name}(models.Model):" in model_file_path.read_text()
    assert f"from .{model_file_name[:-3]} import {model_name}" in init_file_path.read_text()


def test_error_both_models_file_and_folder(tmp_path):
    # Create a mock Django app with both models.py and a models folder
    app_path = create_mock_django_app(
        tmp_path, 
        app_name='testapp',
        with_models_file=True, 
        with_models_folder=True
    )
    runner = CliRunner()
    model_name = "ProductCustomFields"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_model command
    result = runner.invoke(cli, ['testapp', 'create', 'model', model_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about both existing
    assert result.exit_code != 0
    assert "Both 'models.py' and 'models/' folder exist" in result.output


def test_error_no_models_file_or_folder(tmp_path):
    # Create a mock Django app with neither models.py nor models folder
    app_path = create_mock_django_app(
        tmp_path, 
        app_name='testapp',
        with_models_file=False, 
        with_models_folder=False
    )
    runner = CliRunner()
    model_name = "ProductCustomFields"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_model command
    result = runner.invoke(cli, ['testapp', 'create', 'model', model_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about neither existing
    assert result.exit_code != 0
    assert "Neither 'models.py' nor 'models/' folder exists" in result.output

def test_inject_model_without_duplicate_import(tmp_path):
    # Create a mock Django app with models.py that already contains the models import
    app_path = create_mock_django_app(tmp_path, app_name='testapp', with_models_file=True, with_models_folder=False)
    
    # Ensure models.py exists and contains the import
    models_py_path = app_path / 'models.py'
    models_py_path.write_text("from django.db import models\n\n# Existing models\n")

    runner = CliRunner()
    model_name = "TestModelWithoutImport"

    # Run the create_model command to inject the model without adding the import
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'model', model_name])

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "Model 'TestModelWithoutImport' created successfully" in result.output

    # Check the contents of models.py to confirm no duplicate import was added
    content = models_py_path.read_text()
    assert content.count("from django.db import models") == 1
    assert f"class {model_name}(models.Model):" in content

def test_create_model_with_class_dict(tmp_path):
    # Set up a mock Django app in a temporary directory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=False,
        with_models_folder=True
    )

    # Define a single class_dict with imports and class content
    class_dict = {
        "imports": "from django.db import models\nimport uuid\nfrom django.utils import timezone",
        "SampleModel": "class SampleModel(models.Model):\n    name = models.CharField(max_length=100)\n    created_at = models.DateTimeField(default=timezone.now)\n"
    }

    # Extract class name dynamically from the class_dict
    class_name = next(key for key in class_dict.keys() if key != "imports")
    expected_file_name = f"{snake_case(class_name)}.py"

    # Define the expected file path
    model_file_path = app_path / 'models' / expected_file_name

    # Create the models directory and __init__.py if they don't exist
    models_dir = app_path / 'models'
    models_dir.mkdir(exist_ok=True)
    init_file = models_dir / '__init__.py'
    if not init_file.exists():
        init_file.touch()

    # Change to the temp directory
    os.chdir(tmp_path)

    # Run create_model via CLI with class_dict
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ['testapp', 'create', 'model', class_name],
        obj={'app_name': 'testapp', 'class_dict': class_dict},
        catch_exceptions=False
    )

    # Print debug information
    print(f"CLI Result output: {result.output}")
    print(f"Exit code: {result.exit_code}")
    if result.exception:
        print(f"Exception: {result.exception}")
    
    # Print file contents for debugging
    if model_file_path.exists():
        print(f"Model file contents:\n{model_file_path.read_text()}")
    if init_file.exists():
        print(f"Init file contents:\n{init_file.read_text()}")

    # Assertions
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    assert model_file_path.exists(), f"Model file not created at {model_file_path}"
    
    # Check file contents
    file_content = model_file_path.read_text()
    assert class_dict["imports"] in file_content, "Imports not found in model file"
    assert class_dict[class_name] in file_content, "Model class not found in model file"
    
    # Check init file
    assert init_file.exists(), "init file not created"
    init_content = init_file.read_text()
    expected_import = f"from .{snake_case(class_name)} import {class_name}"
    assert expected_import in init_content, f"Expected import '{expected_import}' not found in __init__.py"
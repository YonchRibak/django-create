import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.cli import cli
from django_create.utils import create_mock_django_app, snake_case, Utils

def test_inject_into_serializers_py(tmp_path):
    # Create a mock Django app with serializers.py
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=True,
        with_serializers_folder=False
    )

    # Define the path to serializers.py using Pathlib
    serializers_py_path = app_path / 'serializers.py'
    runner = CliRunner()
    serializer_name = "SomeSerializer"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_serializer command
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Print output for debugging
    print(result.output)
    print(f"Resolved serializers.py path: {serializers_py_path}")
    print(f"serializers.py exists: {serializers_py_path.exists()}")

    # Verify that the serializer was injected into serializers.py
    assert result.exit_code == 0
    assert f"class {serializer_name}(serializers.ModelSerializer):" in serializers_py_path.read_text()


def test_create_in_serializers_folder(tmp_path):
    # Create a mock Django app with a serializers folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=False,
        with_serializers_folder=True
    )

    # Define the paths using Pathlib
    serializers_folder_path = app_path / 'serializers'
    serializer_file_name = "some_serializer.py"
    serializer_file_path = serializers_folder_path / serializer_file_name
    init_file_path = serializers_folder_path / '__init__.py'
    runner = CliRunner()
    serializer_name = "SomeSerializer"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_serializer command
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Print output for debugging
    print(result.output)
    print(f"serializer file path: {serializer_file_path}")
    print(f"serializer file exists: {serializer_file_path.exists()}")

    # Verify that the serializer was created inside the serializers folder
    assert result.exit_code == 0
    assert serializer_file_path.exists()
    assert f"class {serializer_name}(serializers.ModelSerializer):" in serializer_file_path.read_text()
    assert f"from .{serializer_file_name[:-3]} import {serializer_name}" in init_file_path.read_text()


def test_create_in_custom_path(tmp_path):
    # Create a mock Django app with a serializers folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=False,
        with_serializers_folder=True
    )

    # Define the custom path
    custom_path = 'products/some_other_folder'
    custom_serializer_folder_path = app_path / 'serializers' / custom_path
    serializer_file_name = "some_serializer.py"
    serializer_file_path = custom_serializer_folder_path / serializer_file_name
    init_file_path = custom_serializer_folder_path / '__init__.py'
    runner = CliRunner()
    serializer_name = "SomeSerializer"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_serializer command with --path
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name, '--path', custom_path])

    # Print output for debugging
    print(result.output)
    print(f"serializer file path: {serializer_file_path}")
    print(f"serializer file exists: {serializer_file_path.exists()}")

    # Verify that the serializer was created in the custom path
    assert result.exit_code == 0
    assert serializer_file_path.exists()
    assert f"class {serializer_name}(serializers.ModelSerializer):" in serializer_file_path.read_text()
    assert f"from .{serializer_file_name[:-3]} import {serializer_name}" in init_file_path.read_text()


def test_error_both_serializers_file_and_folder(tmp_path):
    # Create a mock Django app with both serializers.py and a serializers folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=True,
        with_serializers_folder=True
    )
    runner = CliRunner()
    serializer_name = "SomeSerializer"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_serializer command
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about both existing
    assert result.exit_code != 0
    assert "Both 'serializers.py' and 'serializers/' folder exist" in result.output


def test_create_when_no_serializers_file_or_folder(tmp_path):
    """Test that serializers.py is created when neither file nor folder exists."""
    # Create a mock Django app with neither serializers.py nor serializers folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=False,
        with_serializers_folder=False
    )

    # Check initial state
    serializers_py_path = app_path / 'serializers.py'
    serializers_folder_path = app_path / 'serializers'
    assert not serializers_py_path.exists(), "serializers.py should not exist initially"
    assert not serializers_folder_path.exists(), "serializers folder should not exist initially"

    runner = CliRunner()
    serializer_name = "SomeSerializer"
    
    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)
    
    # Run the create_serializer command
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Print debug information
    print("\nCommand output:")
    print(result.output)
    print("\nCreated file content:")
    print(serializers_py_path.read_text())

    # Verify successful creation
    assert result.exit_code == 0
    assert f"Serializer '{serializer_name}' created successfully" in result.output

    # Verify serializers.py was created
    assert serializers_py_path.exists(), "serializers.py should be created"
    assert not serializers_folder_path.exists(), "serializers folder should not be created"

    # Verify content of created file
    content = serializers_py_path.read_text()
    assert Utils.DJANGO_IMPORTS['serializers'] in content
    assert f"class {serializer_name}(serializers.ModelSerializer):" in content

def test_inject_serializer_without_duplicate_import(tmp_path):
    # Create a mock Django app with serializers.py that already contains the serializers import
    app_path = create_mock_django_app(tmp_path, app_name='testapp', with_serializers_file=True, with_serializers_folder=False)
    
    # Ensure serializers.py exists and contains the import
    serializers_py_path = app_path / 'serializers.py'
    serializers_py_path.write_text("from rest_framework import serializers\n\n# Existing serializers\n")

    runner = CliRunner()
    serializer_name = "TestSerializerWithoutImport"

    # Run the create_serializer command to inject the serializer without adding the import
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "Serializer 'TestSerializerWithoutImport' created successfully" in result.output

    # Check the contents of serializers.py to confirm no duplicate import was added
    content = serializers_py_path.read_text()
    assert content.count("from rest_framework import serializers") == 1
    assert f"class {serializer_name}(serializers.ModelSerializer):" in content

def test_create_serializer_with_model(tmp_path):
    # Set up a mock Django app in a temporary directory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=False,
        with_serializers_folder=True
    )

    # Define paths for assertions
    serializers_folder_path = app_path / 'serializers'
    serializer_file_name = "user_serializer.py"
    serializer_file_path = serializers_folder_path / serializer_file_name
    init_file_path = serializers_folder_path / "__init__.py"
    runner = CliRunner()

    serializer_name = "UserSerializer"
    model_name = "UserModel"

    # Ensure the file does not initially exist
    assert not serializer_file_path.exists()

    # Run create_serializer via CLI, specifying the --model option
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name, '--model', model_name])

    # Check the CLI command ran successfully
    assert result.exit_code == 0
    assert f"Serializer '{serializer_name}' created successfully" in result.output

    # Verify the serializer file was created with the correct content
    assert serializer_file_path.exists()
    content = serializer_file_path.read_text()
    assert "from rest_framework import serializers" in content
    assert f"from ..models import {model_name}" in content  # Changed from .models to ..models
    assert f"class {serializer_name}(serializers.ModelSerializer):" in content
    
    # Verify that the __init__.py file includes the import for the new serializer
    assert init_file_path.exists()
    init_content = init_file_path.read_text()
    assert f"from .{snake_case(serializer_name)} import {serializer_name}" in init_content

def test_create_serializer_without_model(tmp_path):
    # Set up a mock Django app in a temporary directory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=False,
        with_serializers_folder=True
    )

    # Define paths for assertions
    serializers_folder_path = app_path / 'serializers'
    serializer_file_name = "user_serializer.py"
    serializer_file_path = serializers_folder_path / serializer_file_name
    init_file_path = serializers_folder_path / "__init__.py"
    runner = CliRunner()

    serializer_name = "UserSerializer"

    # Ensure the file does not initially exist
    assert not serializer_file_path.exists()

    # Run create_serializer via CLI without specifying the --model option
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Check the CLI command ran successfully
    assert result.exit_code == 0
    assert f"Serializer '{serializer_name}' created successfully" in result.output

    # Verify the serializer file was created with the placeholder model
    assert serializer_file_path.exists()
    content = serializer_file_path.read_text()
    assert "from rest_framework import serializers" in content
    assert "from ..models import EnterModel" in content  # Changed from .models to ..models
    assert f"class {serializer_name}(serializers.ModelSerializer):" in content

    # Verify that the __init__.py file includes the import for the new serializer
    assert init_file_path.exists()
    init_content = init_file_path.read_text()
    assert f"from .{snake_case(serializer_name)} import {serializer_name}" in init_content

def test_add_serializer_with_model_to_existing_file(tmp_path):
    """Test adding a serializer with model to a file that already has a serializer and imports."""
    # Create a mock Django app with serializers.py containing an existing serializer
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=True,
        with_serializers_folder=False
    )

    # Define initial content for serializers.py with existing serializer
    initial_content = """from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
"""
    # Write this content to serializers.py
    serializers_py_path = app_path / 'serializers.py'
    serializers_py_path.write_text(initial_content)

    # Run the create_serializer command with --model flag
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(
        cli,
        ['testapp', 'create', 'serializer', 'ProductSerializer', '--model', 'Product']
    )

    # Print output for debugging
    print("\nCommand output:")
    print(result.output)
    print("\nResulting file content:")
    print(serializers_py_path.read_text())

    # Verify command execution
    assert result.exit_code == 0
    assert "Serializer 'ProductSerializer' created successfully" in result.output

    # Read the file content
    content = serializers_py_path.read_text()

    # Verify imports and classes after first addition
    assert content.count("from rest_framework import serializers") == 1
    assert content.count("from .models import") == 1
    assert content.count("class UserSerializer(serializers.ModelSerializer):") == 1
    assert content.count("class ProductSerializer(serializers.ModelSerializer):") == 1

    # Check for both models in import, regardless of order
    models_import_line = next(line for line in content.split('\n') if 'from .models import' in line)
    assert 'User' in models_import_line
    assert 'Product' in models_import_line

    # Verify order (imports at top, then classes)
    lines = content.split('\n')
    import_lines = [i for i, line in enumerate(lines) if 'import' in line]
    user_serializer_line = next(i for i, line in enumerate(lines) if 'class UserSerializer' in line)
    product_serializer_line = next(i for i, line in enumerate(lines) if 'class ProductSerializer' in line)

    # Check that all imports come before classes
    assert all(import_line < user_serializer_line for import_line in import_lines)
    assert all(import_line < product_serializer_line for import_line in import_lines)

    # Try adding another serializer with a model that's already imported
    result = runner.invoke(
        cli,
        ['testapp', 'create', 'serializer', 'UserProfileSerializer', '--model', 'User']
    )

    # Verify the final state
    content = serializers_py_path.read_text()
    
    # Check imports haven't been duplicated
    assert content.count("from .models import") == 1
    assert content.count("from rest_framework import serializers") == 1
    
    # Check all three serializer classes exist
    assert content.count("class UserSerializer(serializers.ModelSerializer):") == 1
    assert content.count("class ProductSerializer(serializers.ModelSerializer):") == 1
    assert content.count("class UserProfileSerializer(serializers.ModelSerializer):") == 1
    
    # Check the model statements
    assert content.count("model = User") == 2  # One for UserSerializer, one for UserProfileSerializer
    assert content.count("model = Product") == 1  # One for ProductSerializer

    # Verify imports are still grouped together
    models_import_line = next(line for line in content.split('\n') if 'from .models import' in line)
    assert 'User' in models_import_line
    assert 'Product' in models_import_line

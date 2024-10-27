import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.commands.create_viewset import create_viewset
from django_create.utils import create_mock_django_app, snake_case
from django_create.cli import cli

def test_inject_into_viewsets_py(tmp_path):
    # Create a mock Django app with viewsets.py
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=True,
        with_viewsets_folder=False
    )

    # Define the path to viewsets.py using Pathlib
    viewsets_py_path = app_path / 'viewsets.py'
    runner = CliRunner()
    viewset_name = "SomeViewSet"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_viewset command
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Print output for debugging
    print(result.output)
    print(f"Resolved viewsets.py path: {viewsets_py_path}")
    print(f"viewsets.py exists: {viewsets_py_path.exists()}")

    # Verify that the viewset was injected into viewsets.py
    assert result.exit_code == 0
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in viewsets_py_path.read_text()


def test_create_in_viewsets_folder(tmp_path):
    # Create a mock Django app with a viewsets folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=False,
        with_viewsets_folder=True
    )

    # Define the paths using Pathlib
    viewsets_folder_path = app_path / 'viewsets'
    viewset_file_name = "some_viewset.py"
    viewset_file_path = viewsets_folder_path / viewset_file_name
    init_file_path = viewsets_folder_path / '__init__.py'
    runner = CliRunner()
    viewset_name = "SomeViewSet"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_viewset command
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Print output for debugging
    print(result.output)
    print(f"Viewset file path: {viewset_file_path}")
    print(f"Viewset file exists: {viewset_file_path.exists()}")

    # Verify that the viewset was created inside the viewsets folder
    assert result.exit_code == 0
    assert viewset_file_path.exists()
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in viewset_file_path.read_text()
    assert f"from .{viewset_file_name[:-3]} import {viewset_name}" in init_file_path.read_text()


def test_create_in_custom_path(tmp_path):
    # Create a mock Django app with a viewsets folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=False,
        with_viewsets_folder=True
    )

    # Define the custom path
    custom_path = 'products/some_other_folder'
    custom_viewset_folder_path = app_path / 'viewsets' / custom_path
    viewset_file_name = "some_viewset.py"
    viewset_file_path = custom_viewset_folder_path / viewset_file_name
    init_file_path = custom_viewset_folder_path / '__init__.py'
    runner = CliRunner()
    viewset_name = "SomeViewset"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_viewset command with --path
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name, '--path', custom_path])

    # Print output for debugging
    print(result.output)
    print(f"Viewset file path: {viewset_file_path}")
    print(f"Viewset file exists: {viewset_file_path.exists()}")

    # Verify that the viewset was created in the custom path
    assert result.exit_code == 0
    assert viewset_file_path.exists()
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in viewset_file_path.read_text()
    assert f"from .{viewset_file_name[:-3]} import {viewset_name}" in init_file_path.read_text()


def test_error_both_viewsets_file_and_folder(tmp_path):
    # Create a mock Django app with both viewsets.py and a viewsets folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=True,
        with_viewsets_folder=True
    )
    runner = CliRunner()
    viewset_name = "SomeViewSet"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_viewset command
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about both existing
    assert result.exit_code != 0
    assert "Both 'viewsets.py' and 'viewsets/' folder exist" in result.output


def test_creates_folder_when_none_exist(tmp_path):
    # Create a mock Django app with neither viewsets.py nor viewsets folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=False,
        with_viewsets_folder=False
    )
    runner = CliRunner()
    viewset_name = "SomeViewSet"
    viewsets_folder_path = app_path / 'viewsets'
    viewset_file_name = "some_viewset.py"
    viewset_file_path = viewsets_folder_path / viewset_file_name

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_viewset command
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Print output for debugging
    print(result.output)
    print(f"Viewset file path: {viewset_file_path}")
    print(f"Viewset file exists: {viewset_file_path.exists()}")

    # Verify that the viewsets folder was created, and the viewset file exists inside
    assert result.exit_code == 0
    assert viewsets_folder_path.is_dir()
    assert viewset_file_path.exists()
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in viewset_file_path.read_text()

def test_inject_into_viewsets_py_in_subdirectory(tmp_path):
    # Create a mock Django app with viewsets.py
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=True,
        with_viewsets_folder=False,
        subdirectory='subdir'
    )

    # Define the path to viewsets.py using Pathlib
    viewsets_py_path = app_path / 'viewsets.py'
    runner = CliRunner()
    viewset_name = "SomeViewSet"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_viewset command
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Print output for debugging
    print(result.output)
    print(f"Resolved viewsets.py path: {viewsets_py_path}")
    print(f"viewsets.py exists: {viewsets_py_path.exists()}")

    # Verify that the viewset was injected into viewsets.py
    assert result.exit_code == 0
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in viewsets_py_path.read_text()

def test_inject_viewset_without_duplicate_import(tmp_path):
    # Create a mock Django app with viewsets.py that already contains the viewsets import
    app_path = create_mock_django_app(tmp_path, app_name='testapp', with_viewsets_file=True, with_viewsets_folder=False)
    
    # Ensure viewsets.py exists and contains the import
    viewsets_py_path = app_path / 'viewsets.py'
    viewsets_py_path.write_text("from rest_framework import viewsets\n\n# Existing viewsets\n")

    runner = CliRunner()
    viewset_name = "TestViewSetWithoutImport"

    # Run the create_viewset command to inject the viewset without adding the import
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "Viewset 'TestViewSetWithoutImport' created successfully" in result.output

    # Check the contents of viewsets.py to confirm no duplicate import was added
    content = viewsets_py_path.read_text()
    assert content.count("from rest_framework import viewsets") == 1
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in content

def test_create_viewset_with_model_and_serializer(tmp_path):
    # Set up a mock Django app in a temporary directory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=False,
        with_viewsets_folder=True
    )

    # Define paths for assertions
    viewsets_folder_path = app_path / 'viewsets'
    viewset_file_name = "user_viewset.py"
    viewset_file_path = viewsets_folder_path / viewset_file_name
    init_file_path = viewsets_folder_path / "__init__.py"
    runner = CliRunner()

    viewset_name = "UserViewSet"
    model_name = "UserModel"
    serializer_name = "UserSerializer"

    # Ensure the file does not initially exist
    assert not viewset_file_path.exists()

    # Run create_viewset via CLI with both --model and --serializer options
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name, '--model', model_name, '--serializer', serializer_name])

    # Check the CLI command ran successfully
    assert result.exit_code == 0
    assert f"Viewset '{viewset_name}' created successfully" in result.output

    # Verify the viewset file was created with the correct content
    assert viewset_file_path.exists()
    content = viewset_file_path.read_text()
    assert "from rest_framework import viewsets" in content
    assert f"from .models import {model_name}" in content
    assert f"from .serializers import {serializer_name}" in content
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in content
    assert f"serializer_class = {serializer_name}" in content
    assert f"queryset = {model_name}.objects.all()" in content

    # Verify that the __init__.py file includes the import for the new viewset
    assert init_file_path.exists()
    init_content = init_file_path.read_text()
    assert f"from .{snake_case(viewset_name)} import {viewset_name}" in init_content

def test_create_viewset_without_model_and_serializer(tmp_path):
    # Set up a mock Django app in a temporary directory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_viewsets_file=False,
        with_viewsets_folder=True
    )

    # Define paths for assertions
    viewsets_folder_path = app_path / 'viewsets'
    viewset_file_name = "user_viewset.py"
    viewset_file_path = viewsets_folder_path / viewset_file_name
    init_file_path = viewsets_folder_path / "__init__.py"
    runner = CliRunner()

    viewset_name = "UserViewSet"

    # Ensure the file does not initially exist
    assert not viewset_file_path.exists()

    # Run create_viewset via CLI without specifying --model and --serializer options
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'viewset', viewset_name])

    # Check the CLI command ran successfully
    assert result.exit_code == 0
    assert f"Viewset '{viewset_name}' created successfully" in result.output

    # Verify the viewset file was created with placeholders for model and serializer
    assert viewset_file_path.exists()
    content = viewset_file_path.read_text()
    assert "from rest_framework import viewsets" in content
    assert "from .models import EnterModel" in content  # Default model name used
    assert "from .serializers import EnterSerializer" in content  # Default serializer name used
    assert f"class {viewset_name}(viewsets.ModelViewSet):" in content
    assert "serializer_class = EnterSerializer" in content
    assert "queryset = EnterModel.objects.all()" in content

    # Verify that the __init__.py file includes the import for the new viewset
    assert init_file_path.exists()
    init_content = init_file_path.read_text()
    assert f"from .{snake_case(viewset_name)} import {viewset_name}" in init_content
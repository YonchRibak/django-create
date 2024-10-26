import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.commands.create_viewset import create_viewset
from django_create.utils import create_mock_django_app
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
    viewset_name = "SomeViewset"

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
    viewset_name = "SomeViewset"

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
    viewset_name = "SomeViewset"

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
    viewset_name = "SomeViewset"
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
    viewset_name = "SomeViewset"

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

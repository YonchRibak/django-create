import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.commands.create_view import create_view
from django_create.cli import cli
from django_create.utils import create_mock_django_app

def test_inject_into_views_py(tmp_path):
    # Create a mock Django app with views.py
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=True,
        with_views_folder=False
    )

    # Define the path to views.py using Pathlib
    views_py_path = app_path / 'views.py'
    runner = CliRunner()
    view_name = "SomeView"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_view command
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print output for debugging
    print(result.output)
    print(f"Resolved views.py path: {views_py_path}")
    print(f"views.py exists: {views_py_path.exists()}")

    # Verify that the view was injected into views.py
    assert result.exit_code == 0
    assert f"class {view_name}(View):" in views_py_path.read_text()


def test_create_in_views_folder(tmp_path):
    # Create a mock Django app with a views folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=False,
        with_views_folder=True
    )

    # Define the paths using Pathlib
    views_folder_path = app_path / 'views'
    view_file_name = "some_view.py"
    view_file_path = views_folder_path / view_file_name
    init_file_path = views_folder_path / '__init__.py'
    runner = CliRunner()
    view_name = "SomeView"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_view command
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print output for debugging
    print(result.output)
    print(f"View file path: {view_file_path}")
    print(f"View file exists: {view_file_path.exists()}")

    # Verify that the view was created inside the views folder
    assert result.exit_code == 0
    assert view_file_path.exists()
    assert f"class {view_name}(View):" in view_file_path.read_text()
    assert f"from .{view_file_name[:-3]} import {view_name}" in init_file_path.read_text()


def test_create_in_custom_path(tmp_path):
    # Create a mock Django app with a views folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=False,
        with_views_folder=True
    )

    # Define the custom path
    custom_path = 'products/some_other_folder'
    custom_view_folder_path = app_path / 'views' / custom_path
    view_file_name = "some_view.py"
    view_file_path = custom_view_folder_path / view_file_name
    init_file_path = custom_view_folder_path / '__init__.py'
    runner = CliRunner()
    view_name = "SomeView"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_view command with --path
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name, '--path', custom_path])

    # Print output for debugging
    print(result.output)
    print(f"View file path: {view_file_path}")
    print(f"View file exists: {view_file_path.exists()}")

    # Verify that the view was created in the custom path
    assert result.exit_code == 0
    assert view_file_path.exists()
    assert f"class {view_name}(View):" in view_file_path.read_text()
    assert f"from .{view_file_name[:-3]} import {view_name}" in init_file_path.read_text()


def test_error_both_views_file_and_folder(tmp_path):
    # Create a mock Django app with both views.py and a views folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=True,
        with_views_folder=True
    )
    runner = CliRunner()
    view_name = "SomeView"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_view command
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about both existing
    assert result.exit_code != 0
    assert "Both 'views.py' and 'views/' folder exist" in result.output


def test_error_no_views_file_or_folder(tmp_path):
    # Create a mock Django app with neither views.py nor views folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=False,
        with_views_folder=False
    )
    runner = CliRunner()
    view_name = "SomeView"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_view command
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about neither existing
    assert result.exit_code != 0
    assert "Neither 'views.py' nor 'views/' folder exists" in result.output

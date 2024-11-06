import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.commands.create_view import create_view
from django_create.cli import cli
from django_create.utils import create_mock_django_app, Utils

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

def test_inject_view_without_duplicate_import(tmp_path):
    # Create a mock Django app with views.py that already contains the views import
    app_path = create_mock_django_app(tmp_path, app_name='testapp', with_views_file=True, with_views_folder=False)
    
    # Ensure views.py exists and contains the import
    views_py_path = app_path / 'views.py'
    views_py_path.write_text("from django.db import View\n\nclass SomeView(View):\n")

    runner = CliRunner()
    view_name = "TestViewWithoutImport"

    # Run the create_view command to inject the view without adding the import
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "View 'TestViewWithoutImport' created successfully" in result.output

    # Check the contents of views.py to confirm no duplicate import was added
    content = views_py_path.read_text()
    assert content.count("from django.db import View") == 1
    assert f"class {view_name}(View):" in content

def test_create_view_with_default_content(tmp_path):
    """Test creating a view in a file that only contains Django's default content."""
    # Create a mock Django app
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=True,
        with_views_folder=False
    )

    # Write Django's default content to views.py
    views_py_path = app_path / 'views.py'
    default_content = f"{Utils.DJANGO_IMPORTS['views']}\n\n{Utils.DEFAULT_COMMENTS['views']}\n"
    views_py_path.write_text(default_content)

    # Run the create_view command
    runner = CliRunner()
    os.chdir(tmp_path)
    view_name = "TestView"
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print debug information
    print("\nInitial content:")
    print(default_content)
    print("\nCommand output:")
    print(result.output)
    print("\nFinal content:")
    print(views_py_path.read_text())

    # Verify command execution
    assert result.exit_code == 0
    assert f"View '{view_name}' created successfully" in result.output

    # Read the resulting content
    content = views_py_path.read_text()

    # Since it was default content, the file should be completely overwritten
    assert content.count(Utils.DJANGO_IMPORTS['views']) == 1
    assert Utils.DEFAULT_COMMENTS['views'] not in content
    assert f"class {view_name}(View):" in content

    # Add another view to the file
    second_view = "SecondView"
    result = runner.invoke(cli, ['testapp', 'create', 'view', second_view])

    # Verify second view was added correctly
    content = views_py_path.read_text()
    print("\nContent after second view:")
    print(content)

    # Now it should use injection since file has actual content
    assert content.count(Utils.DJANGO_IMPORTS['views']) == 1  # Import still appears once
    assert f"class {view_name}(View):" in content
    assert f"class {second_view}(View):" in content

    # Try creating a view in a file with non-default but no imports
    non_default_content = "# Custom comment\n\nclass ExistingView(View):\n    pass\n"
    views_py_path.write_text(non_default_content)

    third_view = "ThirdView"
    result = runner.invoke(cli, ['testapp', 'create', 'view', third_view])

    # Verify third view was added with imports
    content = views_py_path.read_text()
    print("\nContent after third view with initial non-default content:")
    print(content)

    assert content.count(Utils.DJANGO_IMPORTS['views']) == 1
    assert "class ExistingView(View):" in content
    assert f"class {third_view}(View):" in content

def test_create_view_with_default_content(tmp_path):
    """Test creating a view in a file that only contains Django's default content."""
    # Create a mock Django app
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_views_file=True,
        with_views_folder=False
    )

    # Write Django's default content to views.py
    views_py_path = app_path / 'views.py'
    default_content = f"{Utils.DJANGO_IMPORTS['views']}\n\n{Utils.DEFAULT_COMMENTS['views']}\n"
    views_py_path.write_text(default_content)

    # Run the create_view command
    runner = CliRunner()
    os.chdir(tmp_path)
    view_name = "TestView"
    result = runner.invoke(cli, ['testapp', 'create', 'view', view_name])

    # Print debug information
    print("\nInitial content:")
    print(default_content)
    print("\nCommand output:")
    print(result.output)
    print("\nFinal content:")
    print(views_py_path.read_text())

    # Verify command execution
    assert result.exit_code == 0
    assert f"View '{view_name}' created successfully" in result.output

    # Read the resulting content
    content = views_py_path.read_text()

    # Since it was default content, the file should be completely overwritten
    assert content.count(Utils.DJANGO_IMPORTS['views']) == 1
    assert Utils.DEFAULT_COMMENTS['views'] not in content
    assert f"class {view_name}(View):" in content

    # Add another view to the file
    second_view = "SecondView"
    result = runner.invoke(cli, ['testapp', 'create', 'view', second_view])

    # Verify second view was added correctly
    content = views_py_path.read_text()
    print("\nContent after second view:")
    print(content)

    # Now it should use injection since file has actual content
    assert content.count(Utils.DJANGO_IMPORTS['views']) == 1  # Import still appears once
    assert f"class {view_name}(View):" in content
    assert f"class {second_view}(View):" in content

    # Try creating a view in a file with non-default but no imports
    non_default_content = "# Custom comment\n\nclass ExistingView(View):\n    pass\n"
    views_py_path.write_text(non_default_content)

    third_view = "ThirdView"
    result = runner.invoke(cli, ['testapp', 'create', 'view', third_view])

    # Verify third view was added with imports
    content = views_py_path.read_text()
    print("\nContent after third view with initial non-default content:")
    print(content)

    assert content.count(Utils.DJANGO_IMPORTS['views']) == 1
    assert "class ExistingView(View):" in content
    assert f"class {third_view}(View):" in content
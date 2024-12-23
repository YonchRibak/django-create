import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.commands.create_test import create_test
from django_create.cli import cli
from django_create.utils import create_mock_django_app, snake_case, Utils

def test_inject_into_tests_py(tmp_path):
    # Create a mock Django app with tests.py
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=True,
        with_tests_folder=False
    )

    # Define the path to tests.py using Pathlib
    tests_py_path = app_path / 'tests.py'
    runner = CliRunner()
    test_name = "SomeTest"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_test command
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print output for debugging
    print(result.output)
    print(f"Resolved tests.py path: {tests_py_path}")
    print(f"tests.py exists: {tests_py_path.exists()}")

    # Verify that the test was injected into tests.py
    assert result.exit_code == 0
    assert f"class {test_name}(TestCase):" in tests_py_path.read_text()
    assert "from rest_framework.test import APIClient" in tests_py_path.read_text()
    assert "from rest_framework import status" in tests_py_path.read_text()
    assert "from django.urls import reverse" in tests_py_path.read_text()



def test_create_in_tests_folder(tmp_path):
    # Create a mock Django app with a tests folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=False,
        with_tests_folder=True
    )

    # Define the paths using Pathlib
    tests_folder_path = app_path / 'tests'
    test_file_name = "test_some_test.py"
    test_file_path = tests_folder_path / test_file_name
    init_file_path = tests_folder_path / '__init__.py'
    runner = CliRunner()
    test_name = "SomeTest"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_test command
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print output for debugging
    print(result.output)
    print(f"test file path: {test_file_path}")
    print(f"test file exists: {test_file_path.exists()}")

    # Verify that the test was created inside the tests folder
    assert result.exit_code == 0
    assert test_file_path.exists()
    assert f"class {test_name}(TestCase):" in test_file_path.read_text()
    assert f"from .{test_file_name[:-3]} import {test_name}" in init_file_path.read_text()


def test_create_in_custom_path(tmp_path):
    # Create a mock Django app with a tests folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=False,
        with_tests_folder=True
    )

    # Define the custom path
    custom_path = 'products/some_other_folder'
    custom_test_folder_path = app_path / 'tests' / custom_path
    test_file_name = "test_some_test.py"
    test_file_path = custom_test_folder_path / test_file_name
    init_file_path = custom_test_folder_path / '__init__.py'
    runner = CliRunner()
    test_name = "SomeTest"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_test command with --path
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name, '--path', custom_path])

    # Print output for debugging
    print(result.output)
    print(f"test file path: {test_file_path}")
    print(f"test file exists: {test_file_path.exists()}")

    # Verify that the test was created in the custom path
    assert result.exit_code == 0
    assert test_file_path.exists()
    assert f"class {test_name}(TestCase):" in test_file_path.read_text()
    assert f"from .{test_file_name[:-3]} import {test_name}" in init_file_path.read_text()


def test_error_both_tests_file_and_folder(tmp_path):
    # Create a mock Django app with both tests.py and a tests folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=True,
        with_tests_folder=True
    )
    runner = CliRunner()
    test_name = "SomeTest"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_test command
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about both existing
    assert result.exit_code != 0
    assert "Both 'tests.py' and 'tests/' folder exist" in result.output


def test_error_no_tests_file_or_folder(tmp_path):
    # Create a mock Django app with neither tests.py nor tests folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=False,
        with_tests_folder=False
    )
    runner = CliRunner()
    test_name = "SomeTest"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_test command
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about neither existing
    assert result.exit_code != 0
    assert "Neither 'tests.py' nor 'tests/' folder exists" in result.output

def test_inject_test_without_duplicate_import(tmp_path):
    # Create a mock Django app with tests.py that already contains the tests import
    app_path = create_mock_django_app(tmp_path, app_name='testapp', with_tests_file=True, with_tests_folder=False)
    
    # Ensure tests.py exists and contains the import
    tests_py_path = app_path / 'tests.py'
    tests_py_path.write_text("from django.test import TestCase\n\n# Existing tests\n")

    runner = CliRunner()
    test_name = "TestTestWithoutImport"

    # Run the create_test command to inject the test without adding the import
    os.chdir(tmp_path)
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "Test 'TestTestWithoutImport' created successfully" in result.output

    # Check the contents of tests.py to confirm no duplicate import was added
    content = tests_py_path.read_text()
    assert content.count("from django.test import TestCase") == 1
    assert f"class {test_name}(TestCase):" in content

def test_create_test_with_default_content(tmp_path):
    """Test creating a test in a file that only contains Django's default content."""
    # Create a mock Django app
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=True,
        with_tests_folder=False
    )

    # Write Django's default content to tests.py
    tests_py_path = app_path / 'tests.py'
    default_content = f"{Utils.DJANGO_IMPORTS['tests']}\n\n{Utils.DEFAULT_COMMENTS['tests']}\n"
    tests_py_path.write_text(default_content)

    # Run the create_test command
    runner = CliRunner()
    os.chdir(tmp_path)
    test_name = "ProductTest"
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print debug information
    print("\nInitial content:")
    print(default_content)
    print("\nCommand output:")
    print(result.output)
    print("\nFinal content:")
    print(tests_py_path.read_text())

    # Verify command execution
    assert result.exit_code == 0
    assert f"test '{test_name}' created successfully" in result.output

    # Read the resulting content
    content = tests_py_path.read_text()

    # Since it was default content, the file should be completely overwritten
    assert content.count(Utils.DJANGO_IMPORTS['tests']) == 1
    assert Utils.DEFAULT_COMMENTS['tests'] not in content
    assert f"class {test_name}(TestCase):" in content

    # Add another test to the file
    second_test = "OrderTest"
    result = runner.invoke(cli, ['testapp', 'create', 'test', second_test])

    # Verify second test was added correctly
    content = tests_py_path.read_text()
    print("\nContent after second test:")
    print(content)

    # Now it should use injection since file has actual content
    assert content.count(Utils.DJANGO_IMPORTS['tests']) == 1  # Import still appears once
    assert f"class {test_name}(TestCase):" in content
    assert f"class {second_test}(TestCase):" in content

    # Check file naming in tests folder case
    tests_folder_path = app_path / 'tests'
    tests_folder_path.mkdir()
    tests_py_path.unlink()  # Remove tests.py

    # Create a test in the folder
    folder_test_name = "CategoryTest"
    result = runner.invoke(cli, ['testapp', 'create', 'test', folder_test_name])

    # Verify file naming
    test_file_path = tests_folder_path / f"test_{snake_case(folder_test_name)}.py"
    assert test_file_path.exists(), f"Expected test file at {test_file_path}"
    content = test_file_path.read_text()
    assert f"class {folder_test_name}(TestCase):" in content

def test_create_test_with_default_content(tmp_path):
    """Test creating a test in a file that only contains Django's default content."""
    # Create a mock Django app
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_tests_file=True,
        with_tests_folder=False
    )

    # Write Django's default content to tests.py
    tests_py_path = app_path / 'tests.py'
    default_content = f"{Utils.DJANGO_IMPORTS['tests']}\n\n{Utils.DEFAULT_COMMENTS['tests']}\n"
    tests_py_path.write_text(default_content)

    # Run the create_test command
    runner = CliRunner()
    os.chdir(tmp_path)
    test_name = "ProductTest"
    result = runner.invoke(cli, ['testapp', 'create', 'test', test_name])

    # Print debug information
    print("\nInitial content:")
    print(default_content)
    print("\nCommand output:")
    print(result.output)
    print("\nFinal content:")
    print(tests_py_path.read_text())

    # Verify command execution
    assert result.exit_code == 0
    assert f"Test '{test_name}' created successfully" in result.output

    # Read the resulting content
    content = tests_py_path.read_text()

    # Since it was default content, the file should be completely overwritten
    assert content.count(Utils.DJANGO_IMPORTS['tests']) == 1
    assert Utils.DEFAULT_COMMENTS['tests'] not in content
    assert f"class {test_name}(TestCase):" in content

    # Add another test to the file
    second_test = "OrderTest"
    result = runner.invoke(cli, ['testapp', 'create', 'test', second_test])

    # Verify second test was added correctly
    content = tests_py_path.read_text()
    print("\nContent after second test:")
    print(content)

    # Now it should use injection since file has actual content
    assert content.count(Utils.DJANGO_IMPORTS['tests']) == 1  # Import still appears once
    assert f"class {test_name}(TestCase):" in content
    assert f"class {second_test}(TestCase):" in content

    # Check file naming in tests folder case
    tests_folder_path = app_path / 'tests'
    tests_folder_path.mkdir()
    tests_py_path.unlink()  # Remove tests.py

    # Create a test in the folder
    folder_test_name = "CategoryTest"
    result = runner.invoke(cli, ['testapp', 'create', 'test', folder_test_name])

    # Verify file naming
    test_file_path = tests_folder_path / f"test_{snake_case(folder_test_name)}.py"
    assert test_file_path.exists(), f"Expected test file at {test_file_path}"
    content = test_file_path.read_text()
    assert f"class {folder_test_name}(TestCase):" in content
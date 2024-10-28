import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.commands.create_test import create_test
from django_create.cli import cli
from django_create.utils import create_mock_django_app

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
    assert "test 'TestTestWithoutImport' created successfully" in result.output

    # Check the contents of tests.py to confirm no duplicate import was added
    content = tests_py_path.read_text()
    assert content.count("from django.test import TestCase") == 1
    assert f"class {test_name}(TestCase):" in content
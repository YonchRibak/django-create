import os
import pytest
from click.testing import CliRunner
from pathlib import Path
from django_create.cli import cli
from django_create.utils import create_mock_django_app

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


def test_error_no_serializers_file_or_folder(tmp_path):
    # Create a mock Django app with neither serializers.py nor serializers folder
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_serializers_file=False,
        with_serializers_folder=False
    )
    runner = CliRunner()
    serializer_name = "SomeSerializer"

    # Change the working directory to the mock environment's base
    os.chdir(tmp_path)

    # Run the create_serializer command
    result = runner.invoke(cli, ['testapp', 'create', 'serializer', serializer_name])

    # Print output for debugging
    print(result.output)

    # Verify that an error is raised about neither existing
    assert result.exit_code != 0
    assert "Neither 'serializers.py' nor 'serializers/' folder exists" in result.output

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
    assert "serializer 'TestSerializerWithoutImport' created successfully" in result.output

    # Check the contents of serializers.py to confirm no duplicate import was added
    content = serializers_py_path.read_text()
    assert content.count("from rest_framework import serializers") == 1
    assert f"class {serializer_name}(serializers.ModelSerializer):" in content
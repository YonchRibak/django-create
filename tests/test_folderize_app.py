import os
import pytest
from click.testing import CliRunner
from django_create.commands.folderize_app import folderize
from django_create.utils import create_mock_django_app

def test_folderize_creates_folders_and_removes_files(tmp_path):
    # Create a mock Django app with models.py, views.py, and tests.py files
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True
    )
    
    # Ensure the files exist before running the command
    assert (app_path / 'models.py').exists()
    assert (app_path / 'views.py').exists()
    assert (app_path / 'tests.py').exists()

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)  # Change directory to ensure correct context for the command
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()

def test_folderize_aborts_if_files_have_class_definitions(tmp_path):
    # Create a mock Django app with models.py containing a class definition
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True
    )
    
    # Write a class definition into models.py
    models_py_path = app_path / 'models.py'
    models_py_path.write_text("class TestModel:\n    pass\n")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command aborted with a warning
    assert result.exit_code == 0
    assert "Warning: 'models.py' contains class definitions. Aborting to prevent data loss." in result.output

    # Verify that the files have not been removed and no folders have been created
    assert models_py_path.exists()
    assert not (app_path / 'models' / '__init__.py').exists()

def test_folderize_aborts_if_app_does_not_exist(tmp_path):
    # Run the folderize command on a non-existent app
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'non_existent_app'})

    # Print output for debugging
    print(result.output)

    # Verify that the command aborts with an error message
    assert result.exit_code == 0
    assert "Error: The app 'non_existent_app' does not exist." in result.output

def test_folderize_works_with_empty_files(tmp_path):
    # Create a mock Django app with empty models.py, views.py, and tests.py files
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True
    )
    
    # Empty the content of each file
    (app_path / 'models.py').write_text("")
    (app_path / 'views.py').write_text("")
    (app_path / 'tests.py').write_text("")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()

def test_folderize_creates_folders_and_removes_files_in_subdirectory(tmp_path):
    # Create a mock Django app in a subdirectory with models.py, views.py, and tests.py files
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True,
        subdirectory='subdir'
    )
    
    # Ensure the files exist before running the command
    assert (app_path / 'models.py').exists()
    assert (app_path / 'views.py').exists()
    assert (app_path / 'tests.py').exists()

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)  # Change directory to ensure correct context for the command
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created in the subdirectory
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()

def test_folderize_aborts_if_app_in_subdirectory_contains_class_definitions(tmp_path):
    # Create a mock Django app with models.py containing a class definition in a subdirectory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True,
        subdirectory='subdir'
    )
    
    # Write a class definition into models.py
    models_py_path = app_path / 'models.py'
    models_py_path.write_text("class TestModel:\n    pass\n")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command aborted with a warning
    assert result.exit_code == 0
    assert "Warning: 'models.py' contains class definitions. Aborting to prevent data loss." in result.output

    # Verify that the files have not been removed and no folders have been created
    assert models_py_path.exists()
    assert not (app_path / 'models' / '__init__.py').exists()

def test_folderize_aborts_if_app_in_subdirectory_does_not_exist(tmp_path):
    # Run the folderize command on a non-existent app in a subdirectory
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'non_existent_app'})

    # Print output for debugging
    print(result.output)

    # Verify that the command aborts with an error message
    assert result.exit_code == 0
    assert "Error: The app 'non_existent_app' does not exist." in result.output

def test_folderize_works_with_empty_files_in_subdirectory(tmp_path):
    # Create a mock Django app with empty models.py, views.py, and tests.py files in a subdirectory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True,
        subdirectory='subdir'
    )
    
    # Empty the content of each file
    (app_path / 'models.py').write_text("")
    (app_path / 'views.py').write_text("")
    (app_path / 'tests.py').write_text("")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created in the subdirectory
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()
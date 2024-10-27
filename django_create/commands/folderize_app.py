import click
import os
import re
from pathlib import Path
from click.testing import CliRunner
from ..utils import extract_file_contents, find_app_path, contains_class_definition
from ..commands import create_model, create_view, create_viewset, create_test, create_serializer

@click.command()
@click.pass_context
def folderize(ctx):
    """
    Organize a Django app by creating folders for models, views, viewsets, and tests.
    Extracts class definitions from any file in the app if present, deletes the original files,
    and re-creates each class in separate files within the respective folders.
    """
    app_name = ctx.obj['app_name']
    click.echo(f"Folderizing app '{app_name}'...")

    base_path = find_app_path(app_name)
    if not base_path:
        click.echo(f"Error: The app '{app_name}' does not exist.")
        return 1

    files_to_process = ['models.py', 'views.py', 'viewsets.py', 'serializers.py', 'tests.py']
    folders_to_create = ['models', 'views', 'viewsets', 'serializers', 'tests']

    # Dictionary to hold extracted classes per file type
    extracted_classes = {}

    # Check each file in files_to_process for class definitions and extract if present
    print("\n=== Processing Files ===")
    for file_name in files_to_process:
        file_path = os.path.join(base_path, file_name)
        print(f"\nProcessing: {file_name}")
        print(f"Path: {file_path}")
        print(f"Exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            if contains_class_definition(file_path):
                print(f"Found classes in {file_name}")
                # Extract content and store in extracted_classes
                extracted_classes[file_name] = extract_file_contents(file_path)
                print(f"Extracted content from {file_name}:")
                print(extracted_classes[file_name])
            os.remove(file_path)  # Remove the original file after extraction
        else:
            click.echo(f"Warning: File '{file_name}' not found, skipping...")

    print("\n=== Creating Folders ===")
    # Create required folders for folderizing
    for folder_name in folders_to_create:
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        init_file = os.path.join(folder_path, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# This file allows the directory to be treated as a Python module.\n")
        print(f"Created folder: {folder_path}")

    print("\n=== Processing Classes ===")
    # Process extracted classes for each file
    for file_name, class_dict in extracted_classes.items():
        print(f"\nProcessing file: {file_name}")
        command_args = []
        if 'model' in file_name:
            command = create_model
            command_args = ['create', 'model']
            print("Using create_model command")
        elif 'view' in file_name and 'viewset' not in file_name:
            command = create_view
            command_args = ['create', 'view']
            print("Using create_view command")
        elif 'viewset' in file_name:
            command = create_viewset
            command_args = ['create', 'viewset']
            print("Using create_viewset command")
        elif 'test' in file_name:
            command = create_test
            command_args = ['create', 'test']
            print("Using create_test command")
        elif 'serializer' in file_name:
            command = create_serializer
            command_args = ['create', 'serializer']
            print("Using create_serializer command")
        else:
            print(f"No matching command for {file_name}")
            continue

        # Extract imports
        imports = class_dict.get("imports", "")

        # Process each class (excluding the "imports" key)
        print(f"Classes to process: {[k for k in class_dict.keys() if k != 'imports']}")
        for class_name in [k for k in class_dict.keys() if k != "imports"]:
            try:
                print(f"\nCreating {class_name}...")
                # Create a new runner for each command
                runner = CliRunner()
                
                # Prepare the context object
                obj = {
                    'app_name': app_name,
                    'class_dict': {
                        "imports": imports,
                        class_name: class_dict[class_name]
                    }
                }
                
                print(f"Context obj: {obj}")
                
                # Run the command using the runner
                result = runner.invoke(
                    command,
                    [class_name],
                    obj=obj,
                    catch_exceptions=False
                )

                if result.exit_code != 0:
                    click.echo(f"Failed to create {class_name}: {result.output}")
                    return 1
                print(f"Successfully created {class_name}")
                click.echo(f"Successfully created {class_name}")
                
            except Exception as e:
                click.echo(f"Error creating {class_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                return 1

    click.echo(f"App '{app_name}' has been folderized successfully.")
    return 0
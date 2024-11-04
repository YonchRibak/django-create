import click
import os
from pathlib import Path
from click.testing import CliRunner
from ..utils import Utils, contains_class_definition, extract_file_contents
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

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
    
    if not app_path.exists():
        # If not found directly, check in each subfolder
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: The app '{app_name}' does not exist.")
            return 1

    module_types = Utils.STANDARD_MODULES
    extracted_classes = {}

    # Process files and extract classes
    print("\n=== Processing Files ===")
    for module_type in module_types:
        file_path = app_path / f"{module_type}.py"
        
        if file_path.exists():
            try:
                if file_path.read_text().strip():  # Check if file is not empty
                    if contains_class_definition(file_path):
                        # Extract content and store in extracted_classes
                        extracted_classes[f"{module_type}.py"] = extract_file_contents(file_path)
                # Remove the original file after extraction
                file_path.unlink()
            except Exception as e:
                click.echo(f"Error processing {module_type}.py: {str(e)}")
        else:
            click.echo(f"Warning: File '{module_type}.py' not found, skipping...")

    # Create required folders
    for folder_name in module_types:
        folder_path = app_path / folder_name
        folder_path.mkdir(exist_ok=True)
        init_file = folder_path / '__init__.py'
        if not init_file.exists():
            init_file.write_text("# This file allows the directory to be treated as a Python module.\n")

    # Map commands to their respective module types
    command_mapping = {
        'models.py': (create_model, ['create', 'model']),
        'views.py': (create_view, ['create', 'view']),
        'viewsets.py': (create_viewset, ['create', 'viewset']),
        'tests.py': (create_test, ['create', 'test']),
        'serializers.py': (create_serializer, ['create', 'serializer'])
    }

    # Process extracted classes for each file
    for file_name, class_dict in extracted_classes.items():
        if file_name not in command_mapping:
            print(f"No matching command for {file_name}")
            continue

        command, command_args = command_mapping[file_name]
        
        # Store imports for the entire file
        imports = class_dict.get("imports", "")

        # Process each class (excluding the "imports" key)
        for class_name in [k for k in class_dict.keys() if k != "imports"]:
            try:
                # Get the class content
                class_content = class_dict[class_name]

                # Create a new class_dict with imports and content
                processed_class_dict = {
                    "imports": imports,
                    class_name: class_content
                }

                # Create a new runner for each command
                runner = CliRunner()
                
                # Prepare the context object
                obj = {
                    'app_name': app_name,
                    'class_dict': processed_class_dict
                }

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
                
            except Exception as e:
                click.echo(f"Error creating {class_name}: {str(e)}")
                import traceback
                traceback.print_exc()
                return 1

    click.echo(f"App '{app_name}' has been folderized successfully.")
    return 0
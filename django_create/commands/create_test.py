import click
from pathlib import Path
import os
from ..utils import Utils, snake_case

@click.command(name='test')
@click.argument('test_name')
@click.option('--path', default=None, help="Subdirectory path inside the tests folder.")
@click.pass_context
def create_test(ctx, test_name, path):
    """
    Create a new Django test in the specified app.

    Example:
        django-create myapp create test SomeTest --path products/some_other_folder
    """
    app_name = ctx.obj['app_name']
    class_dict = ctx.obj.get('class_dict', None)

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name

    if not app_path.exists():
        # If not, check in each subfolder of base_path
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: Could not find app '{app_name}' in {base_path} or any subfolder.")
            return 1
        
    tests_py_path = app_path / 'tests.py'
    tests_folder_path = app_path / 'tests'
    
    # Determine the path for the test file based on the optional --path flag
    if path:
        custom_test_path = tests_folder_path / Path(path)
    else:
        custom_test_path = tests_folder_path

    # Construct the file paths - note the test_ prefix
    test_file_name = f"test_{snake_case(test_name)}.py"
    test_file_path = custom_test_path / test_file_name
    init_file_path = custom_test_path / '__init__.py'

    # Handle class_dict case for folderize
    if class_dict:
        if tests_py_path.exists():
            imports = class_dict.get("imports", "")
            test_content = class_dict.get(test_name, "")
            if imports:
                content = Utils.process_template_imports(
                    imports + "\n\n" + test_content,
                    app_path
                )
            else:
                content = test_content
            Utils.write_or_append_content(tests_py_path, content, 'tests')
        else:
            # Create tests folder structure
            tests_folder_path.mkdir(parents=True, exist_ok=True)
            if path:
                custom_test_path.mkdir(parents=True, exist_ok=True)

            # Process content
            imports = class_dict.get("imports", "")
            test_content = class_dict.get(test_name, "")
            content = Utils.process_template_imports(
                imports + "\n\n" + test_content,
                app_path
            )
            
            # Create files
            Utils.write_or_append_content(test_file_path, content, 'tests')
            init_content = f"from .{test_file_name[:-3]} import {test_name}"
            Utils.write_or_append_content(init_file_path, init_content, 'init')

        click.echo(f"Test '{test_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    test_template_path = templates_path / 'test_template.txt'
    test_template_no_import_path = templates_path / 'test_template_no_import.txt'
    
    if tests_py_path.exists() and not tests_folder_path.exists():
        if Utils.is_default_content(tests_py_path, 'tests'):
          
            # Render full template with imports
            content = Utils.render_template(
                test_template_path,
                app_path,
                test_name=test_name
            )
            Utils.write_or_append_content(tests_py_path, content, 'tests')
        else:
          
            # Check if we need imports
            if Utils.DJANGO_IMPORTS['tests'] in tests_py_path.read_text():
                template_path = test_template_no_import_path
            else:
                template_path = test_template_path
            
            content = Utils.render_template(
                template_path,
                app_path,
                test_name=test_name
            )
            Utils.write_or_append_content(tests_py_path, content, 'tests')
            
    elif tests_folder_path.exists() and not tests_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_test_path.mkdir(parents=True, exist_ok=True)
            
        # Create the test file with full template
        content = Utils.render_template(
            test_template_path,
            app_path,
            test_name=test_name
        )
        Utils.write_or_append_content(test_file_path, content, 'tests')

        # Add import to __init__.py
        init_content = f"from .{test_file_name[:-3]} import {test_name}"
        Utils.write_or_append_content(init_file_path, init_content, 'init')
        
    elif tests_py_path.exists() and tests_folder_path.exists():
        raise click.ClickException(
            "Both 'tests.py' and 'tests/' folder exist. Please remove one before proceeding."
        )
    else:
        raise click.ClickException(
            "Neither 'tests.py' nor 'tests/' folder exists. Please create one before proceeding."
        )

    click.echo(f"Test '{test_name}' created successfully in app '{app_name}'.")
    return 0
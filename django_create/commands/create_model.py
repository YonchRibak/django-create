import click
from pathlib import Path
import os
from ..utils import (
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    render_template,
    is_import_in_file
)

@click.command(name='model')
@click.argument('model_name')
@click.option('--path', default=None, help="Subdirectory path inside the models folder.")
@click.pass_context
def create_model(ctx, model_name, path):
    """
    Create a new Django model in the specified app.

    Example:
        django-create myapp create model SomeModel --path products/some_other_folder
    """
    app_name = ctx.obj['app_name']
    class_dict = ctx.obj.get('class_dict', None)  # Retrieve class_dict from ctx.obj
    # print(f"class_dict in create_model: {class_dict}")  # Verify class_dict is passed
    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
    
    if not app_path.exists():
        # If not, check in each subfolder of base_path
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: Could not find app '{app_name}' in {base_path} or any subfolder.")
            return
        
    models_py_path = app_path / 'models.py'
    models_folder_path = app_path / 'models'
    
    # Determine the path for the model file based on the optional --path flag
    if path:
        custom_model_path = models_folder_path / Path(path)
    else:
        custom_model_path = models_folder_path


    # Construct the file paths
    model_file_name = f"{snake_case(model_name)}.py"
    model_file_path = custom_model_path / model_file_name
    init_file_path = custom_model_path / '__init__.py'


    # Write models from class_dict if provided
    if class_dict:
        print(f"Debug: Received class_dict: {class_dict}")  # Temporary for debug
        imports = class_dict.get("imports", "")
        model_content = class_dict.get(model_name, "")
        full_content = imports + "\n\n" + model_content
        create_element_file(model_file_path, full_content)
    
        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, model_name, model_file_name)

        return
    
    # Define the path to the model template
    templates_path = Path(__file__).parent.parent / 'templates'
    model_template_path = templates_path / 'model_template.txt'
    model_template_no_import_path = templates_path / 'model_template_no_import.txt'
    model_content = render_template(model_template_path, model_name=model_name)
    model_content_no_import = render_template(model_template_no_import_path, model_name=model_name)
    
    if models_py_path.exists() and not models_folder_path.exists():
        if is_import_in_file(models_py_path, 'from django.db import models'):
            inject_element_into_file(models_py_path, model_content_no_import)
        else:
            inject_element_into_file(models_py_path,model_content)
    elif models_folder_path.exists() and not models_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_model_path.mkdir(parents=True, exist_ok=True)

        # Create the model file inside the specified or default folder
        create_element_file(model_file_path, model_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, model_name, model_file_name)
    elif models_py_path.exists() and models_folder_path.exists():
        raise click.ClickException(
            "Both 'models.py' and 'models/' folder exist. Please remove one before proceeding."
    )
    else:
        raise click.ClickException(
            "Neither 'models.py' nor 'models/' folder exists. Please create one before proceeding."
        )

    click.echo(f"Model '{model_name}' created successfully in app '{app_name}'.")

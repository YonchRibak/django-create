import click
from pathlib import Path
import os
from ..utils import Utils, snake_case

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

    # Handle class_dict case for folderize
    if class_dict:
        if models_py_path.exists():
            imports = class_dict.get("imports", "")
            model_content = class_dict.get(model_name, "")
            if imports:
                content = Utils.process_template_imports(
                    imports + "\n\n" + model_content, 
                    app_path
                )
            else:
                content = model_content
            Utils.write_or_append_content(models_py_path, content, 'models')
        else:
            # Create models folder structure
            models_folder_path.mkdir(parents=True, exist_ok=True)
            if path:
                custom_model_path.mkdir(parents=True, exist_ok=True)

            # Process content
            imports = class_dict.get("imports", "")
            model_content = class_dict.get(model_name, "")
            content = Utils.process_template_imports(
                imports + "\n\n" + model_content, 
                app_path
            )
            
            # Create files
            Utils.write_or_append_content(model_file_path, content, 'models')
            init_content = f"from .{model_file_name[:-3]} import {model_name}"
            Utils.write_or_append_content(init_file_path, init_content, 'init')

        click.echo(f"Model '{model_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    model_template_path = templates_path / 'model_template.txt'
    model_template_no_import_path = templates_path / 'model_template_no_import.txt'
    
    if models_py_path.exists() and not models_folder_path.exists():
        if Utils.is_default_content(models_py_path, 'models'):
            # Render full template with imports
            content = Utils.render_template(
                model_template_path, 
                app_path, 
                model_name=model_name
            )
            Utils.write_or_append_content(models_py_path, content, 'models')
        else:
            # Check if we need imports
            if Utils.DJANGO_IMPORTS['models'] in models_py_path.read_text():
                template_path = model_template_no_import_path
            else:
                template_path = model_template_path
            
            content = Utils.render_template(
                template_path, 
                app_path, 
                model_name=model_name
            )
            Utils.write_or_append_content(models_py_path, content, 'models')
            
    elif models_folder_path.exists() and not models_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_model_path.mkdir(parents=True, exist_ok=True)
            
        # Create the model file with full template
        content = Utils.render_template(
            model_template_path, 
            app_path, 
            model_name=model_name
        )
        Utils.write_or_append_content(model_file_path, content, 'models')

        # Add import to __init__.py
        init_content = f"from .{model_file_name[:-3]} import {model_name}"
        Utils.write_or_append_content(init_file_path, init_content, 'init')
        
    elif models_py_path.exists() and models_folder_path.exists():
        raise click.ClickException(
            "Both 'models.py' and 'models/' folder exist. Please remove one before proceeding."
        )
    else:
        raise click.ClickException(
            "Neither 'models.py' nor 'models/' folder exists. Please create one before proceeding."
        )

    click.echo(f"Model '{model_name}' created successfully in app '{app_name}'.")
    return 0
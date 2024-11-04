import click
from pathlib import Path
import os
from ..utils import Utils, snake_case

@click.command(name='view')
@click.argument('view_name')
@click.option('--path', default=None, help="Subdirectory path inside the views folder.")
@click.pass_context
def create_view(ctx, view_name, path):
    """
    Create a new Django view in the specified app.

    Example:
        django-create myapp create view SomeView --path products/some_other_folder
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
        
    views_py_path = app_path / 'views.py'
    views_folder_path = app_path / 'views'
    
    # Determine the path for the view file based on the optional --path flag
    if path:
        custom_view_path = views_folder_path / Path(path)
    else:
        custom_view_path = views_folder_path

    # Construct the file paths
    view_file_name = f"{snake_case(view_name)}.py"
    view_file_path = custom_view_path / view_file_name
    init_file_path = custom_view_path / '__init__.py'

    # Handle class_dict case for folderize
    if class_dict:
        if views_py_path.exists():
            imports = class_dict.get("imports", "")
            view_content = class_dict.get(view_name, "")
            if imports:
                content = Utils.process_template_imports(
                    imports + "\n\n" + view_content, 
                    app_path
                )
            else:
                content = view_content
            Utils.write_or_append_content(views_py_path, content, 'views')
        else:
            # Create views folder structure
            views_folder_path.mkdir(parents=True, exist_ok=True)
            if path:
                custom_view_path.mkdir(parents=True, exist_ok=True)

            # Process content
            imports = class_dict.get("imports", "")
            view_content = class_dict.get(view_name, "")
            content = Utils.process_template_imports(
                imports + "\n\n" + view_content, 
                app_path
            )
            
            # Create files
            Utils.write_or_append_content(view_file_path, content, 'views')
            init_content = f"from .{view_file_name[:-3]} import {view_name}"
            Utils.write_or_append_content(init_file_path, init_content, 'init')

        click.echo(f"View '{view_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    view_template_path = templates_path / 'view_template.txt'
    view_template_no_import_path = templates_path / 'view_template_no_import.txt'
    
    if views_py_path.exists() and not views_folder_path.exists():
        if Utils.is_default_content(views_py_path, 'views'):
            # Render full template with imports
            content = Utils.render_template(
                view_template_path, 
                app_path, 
                view_name=view_name
            )
            Utils.write_or_append_content(views_py_path, content, 'views')
        else:
            # Check if we need imports
            if Utils.DJANGO_IMPORTS['views'] in views_py_path.read_text():
                template_path = view_template_no_import_path
            else:
                template_path = view_template_path
            
            content = Utils.render_template(
                template_path, 
                app_path, 
                view_name=view_name
            )
            Utils.write_or_append_content(views_py_path, content, 'views')
            
    elif views_folder_path.exists() and not views_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_view_path.mkdir(parents=True, exist_ok=True)
            
        # Create the view file with full template
        content = Utils.render_template(
            view_template_path, 
            app_path, 
            view_name=view_name
        )
        Utils.write_or_append_content(view_file_path, content, 'views')

        # Add import to __init__.py
        init_content = f"from .{view_file_name[:-3]} import {view_name}"
        Utils.write_or_append_content(init_file_path, init_content, 'init')
        
    elif views_py_path.exists() and views_folder_path.exists():
        raise click.ClickException(
            "Both 'views.py' and 'views/' folder exist. Please remove one before proceeding."
        )
    else:
        raise click.ClickException(
            "Neither 'views.py' nor 'views/' folder exists. Please create one before proceeding."
        )

    click.echo(f"View '{view_name}' created successfully in app '{app_name}'.")
    return 0
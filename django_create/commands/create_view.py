import click
from pathlib import Path
import os
from ..utils import (
    Utils,
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    render_template,
    is_import_in_file,
    modify_import_statement_to_double_dot
)

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

    # Handle class_dict case
    if class_dict:
        if views_py_path.exists():
            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            view_content = class_dict.get(view_name, "")
            full_content = imports + "\n\n" + view_content
            inject_element_into_file(views_py_path, full_content)
        else:
            # Create views folder if needed
            views_folder_path.mkdir(parents=True, exist_ok=True)
            
            # Set up paths
            if path:
                custom_view_path.mkdir(parents=True, exist_ok=True)

            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            view_content = class_dict.get(view_name, "")
            full_content = imports + "\n\n" + view_content
            create_element_file(view_file_path, full_content)
            add_import_to_file(init_file_path, view_name, view_file_name)

        click.echo(f"View '{view_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    view_template_path = templates_path / 'view_template.txt'
    view_template_no_import_path = templates_path / 'view_template_no_import.txt'
    view_content = render_template(view_template_path, view_name=view_name)
    view_content_no_import = render_template(view_template_no_import_path, view_name=view_name)
    
    if views_py_path.exists() and not views_folder_path.exists():
        if Utils.is_default_content(views_py_path, 'views'):
            # If only default content exists, overwrite the file
            with open(views_py_path, 'w') as f:
                f.write(view_content)
        else:
            # File has actual views, check for import
            if is_import_in_file(views_py_path, Utils.DJANGO_IMPORTS['views']):
                inject_element_into_file(views_py_path, view_content_no_import)
            else:
                inject_element_into_file(views_py_path, view_content)
    elif views_folder_path.exists() and not views_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_view_path.mkdir(parents=True, exist_ok=True)
            
        # Create the view file inside the specified or default folder
        create_element_file(view_file_path, view_content)

        # Add import to __init__.py at the specified path
        add_import_to_file(init_file_path, view_name, view_file_name)
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
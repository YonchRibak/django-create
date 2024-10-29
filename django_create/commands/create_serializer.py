import click
from pathlib import Path
import os
from ..utils import (
    Utils,
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    add_import,
    render_template,
    is_import_in_file,
    modify_import_statement_to_double_dot,
    )

@click.command(name='serializer')
@click.argument('serializer_name')
@click.option('--path', default=None, help="Subdirectory path inside the serializers folder.")
@click.option('--model', default=None, help="Specify the model to be used in the serializer.")
@click.pass_context
def create_serializer(ctx, serializer_name, path, model):
    """
    Create a new Django serializer in the specified app.

    Example:
        django-create myapp create serializer SomeSerializer --path products/some_other_folder --model Product
    """
    app_name = ctx.obj['app_name']
    class_dict = ctx.obj.get('class_dict', None)

    # Use the current working directory as the base path
    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name

    if not app_path.exists():
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: Could not find app '{app_name}' in {base_path} or any subfolder.")
            return 1
        
    serializers_py_path = app_path / 'serializers.py'
    serializers_folder_path = app_path / 'serializers'

    # Check for conflicting files/folders first
    if serializers_py_path.exists() and serializers_folder_path.exists():
        raise click.ClickException(
            "Both 'serializers.py' and 'serializers/' folder exist. Please remove one before proceeding."
        )
    
    # Handle class_dict case for folderize command
    if class_dict:
        if serializers_py_path.exists():
            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            serializer_content = class_dict.get(serializer_name, "")
            if not serializer_content:
                click.echo(f"Error: No content found for serializer {serializer_name}")
                return 1
            full_content = imports + "\n\n" + serializer_content
            inject_element_into_file(serializers_py_path, full_content)
        else:
            # Create serializers folder if needed
            serializers_folder_path.mkdir(parents=True, exist_ok=True)
            
            # Set up paths
            if path:
                custom_serializer_path = serializers_folder_path / Path(path)
                custom_serializer_path.mkdir(parents=True, exist_ok=True)
            else:
                custom_serializer_path = serializers_folder_path

            serializer_file_name = f"{snake_case(serializer_name)}.py"
            serializer_file_path = custom_serializer_path / serializer_file_name
            init_file_path = custom_serializer_path / '__init__.py'

            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            serializer_content = class_dict.get(serializer_name, "")
            if not serializer_content:
                click.echo(f"Error: No content found for serializer {serializer_name}")
                return 1
            full_content = imports + "\n\n" + serializer_content
            create_element_file(serializer_file_path, full_content)
            add_import_to_file(init_file_path, serializer_name, serializer_file_name)

        click.echo(f"Serializer '{serializer_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    model_name = model or "EnterModel"
    
    if serializers_py_path.exists() and not serializers_folder_path.exists():
        if Utils.is_default_content(serializers_py_path, 'serializers'):
            # If only default content exists, overwrite the file
            template = templates_path / 'serializer_template.txt'
            content = render_template(template, serializer_name=serializer_name, model_name=model_name)
            with open(serializers_py_path, 'w') as f:
                f.write(content)
        else:
            # Add required imports
            if not is_import_in_file(serializers_py_path, Utils.DJANGO_IMPORTS['serializers']):
                add_import(serializers_py_path, Utils.DJANGO_IMPORTS['serializers'])
            
            # Add model import if specified
            if model:
                add_import(serializers_py_path, f'from .models import {model}')

            # Render and inject the serializer content without imports
            template_no_import = templates_path / 'serializer_template_no_import.txt'
            content = render_template(template_no_import, serializer_name=serializer_name, model_name=model_name)
            inject_element_into_file(serializers_py_path, content)

    elif serializers_folder_path.exists() and not serializers_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_serializer_path = serializers_folder_path / Path(path)
            custom_serializer_path.mkdir(parents=True, exist_ok=True)
        else:
            custom_serializer_path = serializers_folder_path

        serializer_file_name = f"{snake_case(serializer_name)}.py"
        serializer_file_path = custom_serializer_path / serializer_file_name
        init_file_path = custom_serializer_path / '__init__.py'

        # Create the serializer file with full template
        template = templates_path / 'serializer_template.txt'
        content = render_template(template, serializer_name=serializer_name, model_name=model_name)
        create_element_file(serializer_file_path, content)
        add_import_to_file(init_file_path, serializer_name, serializer_file_name)
    else:
        # Neither exists, create serializers.py by default
        template = templates_path / 'serializer_template.txt'
        content = render_template(template, serializer_name=serializer_name, model_name=model_name)
        with open(serializers_py_path, 'w') as f:
            f.write(content)

    click.echo(f"Serializer '{serializer_name}' created successfully in app '{app_name}'.")
    return 0
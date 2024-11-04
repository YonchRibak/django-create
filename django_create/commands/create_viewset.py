import click
from pathlib import Path
import os
from ..utils import Utils, snake_case

@click.command(name='viewset')
@click.argument('viewset_name')
@click.option('--path', default=None, help="Subdirectory path inside the viewsets folder.")
@click.option('--model', default=None, help="Model name to insert into template.")
@click.option('--serializer', default=None, help="Serializer name to import into template.")
@click.pass_context
def create_viewset(ctx, viewset_name, path, model, serializer):
    """
    Create a new Django viewset in the specified app.

    Example:
        django-create myapp create viewset SomeViewset --path products/some_other_folder --model Product
    """
    app_name = ctx.obj['app_name']
    class_dict = ctx.obj.get('class_dict', None)

    base_path = Path(os.getcwd()).resolve()
    app_path = base_path / app_name
    
    if not app_path.exists():
        possible_paths = [folder / app_name for folder in base_path.iterdir() if folder.is_dir()]
        app_path = next((p for p in possible_paths if p.exists()), None)
        
        if not app_path:
            click.echo(f"Error: Could not find app '{app_name}' in {base_path} or any subfolder.")
            return 1
    
    viewsets_py_path = app_path / 'viewsets.py'
    viewsets_folder_path = app_path / 'viewsets'

    # Check for conflicting files/folders first
    if viewsets_py_path.exists() and viewsets_folder_path.exists():
        raise click.ClickException(
            "Both 'viewsets.py' and 'viewsets/' folder exist. Please remove one before proceeding."
        )
    
    # Handle class_dict case for folderize
    if class_dict:
        if viewsets_py_path.exists():
            imports = class_dict.get("imports", "")
            viewset_content = class_dict.get(viewset_name, "")
            if not viewset_content:
                click.echo(f"Error: No content found for viewset {viewset_name}")
                return 1
                
            if imports:
                content = Utils.process_template_imports(
                    imports + "\n\n" + viewset_content,
                    app_path
                )
            else:
                content = viewset_content
            Utils.write_or_append_content(viewsets_py_path, content, 'viewsets')
        else:
            # Create viewsets folder structure
            viewsets_folder_path.mkdir(parents=True, exist_ok=True)
            if path:
                custom_viewset_path = viewsets_folder_path / Path(path)
                custom_viewset_path.mkdir(parents=True, exist_ok=True)
            else:
                custom_viewset_path = viewsets_folder_path

            viewset_file_name = f"{snake_case(viewset_name)}.py"
            viewset_file_path = custom_viewset_path / viewset_file_name
            init_file_path = custom_viewset_path / '__init__.py'

            imports = class_dict.get("imports", "")
            viewset_content = class_dict.get(viewset_name, "")
            content = Utils.process_template_imports(
                imports + "\n\n" + viewset_content,
                app_path
            )
            
            Utils.write_or_append_content(viewset_file_path, content, 'viewsets')
            init_content = f"from .{viewset_file_name[:-3]} import {viewset_name}"
            Utils.write_or_append_content(init_file_path, init_content, 'init')

        click.echo(f"Viewset '{viewset_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    model_name = model or "EnterModel"
    serializer_name = serializer or "EnterSerializer"

    # Determine import style based on existing content or folder structure
    import_style = '..'
    if viewsets_py_path.exists():
        content = viewsets_py_path.read_text()
        if 'from .models import' in content:
            import_style = '.'
        elif 'from ..models import' in content:
            import_style = '..'
    elif not viewsets_folder_path.exists() and not path:
        import_style = '.'

    # Prepare content based on import style
    template = templates_path / 'viewset_template.txt'
    content = Utils.render_template(
        template,
        app_path,
        viewset_name=viewset_name,
        model_name=model_name,
        serializer_name=serializer_name
    )
    content = content.replace('from .models', f'from {import_style}models')
    content = content.replace('from .serializers', f'from {import_style}serializers')

    if viewsets_py_path.exists() and not viewsets_folder_path.exists():
        Utils.write_or_append_content(viewsets_py_path, content, 'viewsets')
    elif viewsets_folder_path.exists() or path:
        # Ensure the custom path exists if provided
        if path:
            custom_viewset_path = viewsets_folder_path / Path(path)
            custom_viewset_path.mkdir(parents=True, exist_ok=True)
        else:
            custom_viewset_path = viewsets_folder_path

        viewset_file_name = f"{snake_case(viewset_name)}.py"
        viewset_file_path = custom_viewset_path / viewset_file_name
        init_file_path = custom_viewset_path / '__init__.py'

        # Create the viewset file
        Utils.write_or_append_content(viewset_file_path, content, 'viewsets')

        # Add import to __init__.py
        init_content = f"from .{viewset_file_name[:-3]} import {viewset_name}"
        Utils.write_or_append_content(init_file_path, init_content, 'init')
    else:
        Utils.write_or_append_content(viewsets_py_path, content, 'viewsets')

    click.echo(f"Viewset '{viewset_name}' created successfully in app '{app_name}'.")
    return 0
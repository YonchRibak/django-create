import click
from pathlib import Path
import os
from ..utils import Utils, snake_case

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

    # Handle class_dict case for folderize
    if class_dict:
        serializer_content = class_dict.get(serializer_name, "")
        if not serializer_content:
            click.echo(f"Error: No content found for serializer {serializer_name}")
            return 1
            
        if serializers_py_path.exists():
            imports = class_dict.get("imports", "")
            if imports:
                content = Utils.process_template_imports(
                    imports + "\n\n" + serializer_content,
                    app_path
                )
            else:
                content = serializer_content
            Utils.write_or_append_content(serializers_py_path, content, 'serializers')
        else:
            # Create serializers folder structure
            serializers_folder_path.mkdir(parents=True, exist_ok=True)
            if path:
                custom_serializer_path = serializers_folder_path / Path(path)
                custom_serializer_path.mkdir(parents=True, exist_ok=True)
            else:
                custom_serializer_path = serializers_folder_path

            serializer_file_name = f"{snake_case(serializer_name)}.py"
            serializer_file_path = custom_serializer_path / serializer_file_name
            init_file_path = custom_serializer_path / '__init__.py'

            # Process content
            imports = class_dict.get("imports", "")
            content = Utils.process_template_imports(
                imports + "\n\n" + serializer_content,
                app_path
            )
            
            # Create files
            Utils.write_or_append_content(serializer_file_path, content, 'serializers')
            init_content = f"from .{serializer_file_name[:-3]} import {serializer_name}"
            Utils.write_or_append_content(init_file_path, init_content, 'init')

        click.echo(f"Serializer '{serializer_name}' created successfully in app '{app_name}'.")
        return 0

    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    model_name = model or "EnterModel"

    if serializers_py_path.exists() and not serializers_folder_path.exists():
        if Utils.is_default_content(serializers_py_path, 'serializers'):
            # If only default content exists, overwrite the file
            template = templates_path / 'serializer_template.txt'
            content = Utils.render_template(
                template,
                app_path,
                serializer_name=serializer_name,
                model_name=model_name
            )
            Utils.write_or_append_content(serializers_py_path, content, 'serializers')
        else:
            # Add serializer content
            template = templates_path / 'serializer_template_no_import.txt'
            serializer_content = Utils.render_template(
                template,
                app_path,
                serializer_name=serializer_name,
                model_name=model_name
            )
            
            # Check existing content
            current_content = serializers_py_path.read_text()
            
            # Prepare imports
            imports = ["from rest_framework import serializers"]
            
            # Handle model imports by consolidating them
            current_models = []
            import_prefix = None
            lines = current_content.split('\n')
            for line in lines:
                if line.startswith(('from .models import', 'from ..models import')):
                    import_prefix = line.split('import')[0].strip()
                    current_models.extend(model.strip() for model in line.split('import')[1].strip().split(', '))
            
            if current_models:
                # Add new model to existing models if needed
                if model_name not in current_models:
                    current_models.append(model_name)
                import_prefix = import_prefix or 'from .models'
                models_import = f"{import_prefix} import {', '.join(sorted(set(current_models)))}"
                imports.append(models_import)
            else:
                # No existing models import
                imports.append(f"from .models import {model_name}")
            
            # Combine imports and content
            content = '\n'.join(imports) + '\n\n' + serializer_content
            Utils.write_or_append_content(serializers_py_path, content, 'serializers')

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
        content = Utils.render_template(
            template,
            app_path,
            serializer_name=serializer_name,
            model_name=model_name
        )
        # For folder structure, we want double-dot imports
        content = content.replace("from .models", "from ..models")
        Utils.write_or_append_content(serializer_file_path, content, 'serializers')
        
        # Add import to __init__.py
        init_content = f"from .{serializer_file_name[:-3]} import {serializer_name}"
        Utils.write_or_append_content(init_file_path, init_content, 'init')
    else:
        # Neither exists, create serializers.py by default
        template = templates_path / 'serializer_template.txt'
        content = Utils.render_template(
            template,
            app_path,
            serializer_name=serializer_name,
            model_name=model_name
        )
        Utils.write_or_append_content(serializers_py_path, content, 'serializers')

    click.echo(f"Serializer '{serializer_name}' created successfully in app '{app_name}'.")
    return 0
import click
from pathlib import Path
import os
from ..utils import (
    snake_case,
    inject_element_into_file,
    create_element_file,
    add_import_to_file,
    add_import,
    render_template,
    modify_import_statement_to_double_dot,
    merge_item_into_import,
    is_import_in_file, 
    Utils
    
)

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
        django-create myapp create viewset SomeViewset --path products/some_other_folder --model Product --serializer ProductSerializer
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
    
    viewsets_py_path = app_path / 'viewsets.py'
    viewsets_folder_path = app_path / 'viewsets'

    # Check for conflicting files/folders first
    if viewsets_py_path.exists() and viewsets_folder_path.exists():
        raise click.ClickException(
            "Both 'viewsets.py' and 'viewsets/' folder exist. Please remove one before proceeding."
        )
    
    # Handle class_dict case
    if class_dict:
        if viewsets_py_path.exists():
            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            viewset_content = class_dict.get(viewset_name, "")
            full_content = imports + "\n\n" + viewset_content
            inject_element_into_file(viewsets_py_path, full_content)
        else:
            # Create viewsets folder if needed
            viewsets_folder_path.mkdir(parents=True, exist_ok=True)
            
            # Set up paths
            if path:
                custom_viewset_path = viewsets_folder_path / Path(path)
                custom_viewset_path.mkdir(parents=True, exist_ok=True)
            else:
                custom_viewset_path = viewsets_folder_path

            viewset_file_name = f"{snake_case(viewset_name)}.py"
            viewset_file_path = custom_viewset_path / viewset_file_name
            init_file_path = custom_viewset_path / '__init__.py'

            imports = class_dict.get("imports", "")
            if imports:
                import_lines = imports.split('\n')
                modified_import_lines = [modify_import_statement_to_double_dot(line) for line in import_lines]
                imports = '\n'.join(modified_import_lines)
            viewset_content = class_dict.get(viewset_name, "")
            full_content = imports + "\n\n" + viewset_content
            create_element_file(viewset_file_path, full_content)
            add_import_to_file(init_file_path, viewset_name, viewset_file_name)

        click.echo(f"Viewset '{viewset_name}' created successfully in app '{app_name}'.")
        return 0
    
    # Template-based creation
    templates_path = Path(__file__).parent.parent / 'templates'
    model_name = model or "EnterModel"
    serializer_name = serializer or "EnterSerializer"

    if viewsets_py_path.exists() and not viewsets_folder_path.exists():
        if Utils.is_default_content(viewsets_py_path, 'viewsets'):
            # If only default content exists, overwrite the file
            template = templates_path / 'viewset_template.txt'
            content = render_template(template, viewset_name=viewset_name, serializer_name=serializer_name, model_name=model_name)
            with open(viewsets_py_path, 'w') as f:
                f.write(content)
        else:
            if model:
                model_import_line = f"from ..models import {model}"
                with open(viewsets_py_path, 'r') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('from ..models') or line.startswith('from .models'):
                        if model not in line:
                            merged_line = merge_item_into_import(line, model, 'from ..models')
                            lines[i] = merged_line
                            with open(viewsets_py_path, 'w') as f:
                                f.writelines(lines)
                    else: 
                        add_import(viewsets_py_path, model_import_line)

            if serializer:
                serializer_import_line = f"from ..serializers import {serializer}"
                with open(viewsets_py_path, 'r') as f:
                    lines = f.readlines()
        
                for i, line in enumerate(lines):
                    if line.startswith('from ..serializers') or line.startswith('from .serializers'):
                        if serializer not in line:
                            merged_line = merge_item_into_import(line, serializer, 'from ..serializers')
                            lines[i] = merged_line
                            with open(viewsets_py_path, 'w') as f:
                                f.writelines(lines)
                    else:    
                        add_import(viewsets_py_path, serializer_import_line) 
            
             # Render and inject the serializer content without imports
            template_no_import = templates_path / 'viewset_template_no_import.txt'
            content = render_template(template_no_import, viewset_name=viewset_name, serializer_name=serializer_name, model_name=model_name)
            inject_element_into_file(viewsets_py_path, content)
        
    elif viewsets_folder_path.exists() and not viewsets_py_path.exists():
        # Ensure the custom path exists if provided
        if path:
            custom_viewset_path = viewsets_folder_path / Path(path)
            custom_viewset_path.mkdir(parents=True, exist_ok=True)
        else:
            custom_viewset_path = viewsets_folder_path

        viewset_file_name = f'{snake_case(viewset_name)}.py'
        viewset_file_path = custom_viewset_path / viewset_file_name
        init_file_path = custom_viewset_path / '__init__.py'

        # Create the serializer file with full template
        template = templates_path / 'viewset_template.txt'
        content = render_template(template, viewset_name=viewset_name,serializer_name=serializer_name, model_name=model_name)
        create_element_file(viewset_file_path, content)
        add_import_to_file(init_file_path, viewset_name, viewset_file_name)
    else: 
        # Neither exists, create viewsets.py by default
        template = templates_path / 'viewset_template.txt'
        content = render_template(template, viewset_name=viewset_name, serializer_name=serializer_name, model_name=model_name)
        with open(viewsets_py_path, 'w') as f:
            f.write(content)
        # # Check if the required imports are already in the file
        # if model:
        #     model_import_line = f"from ..models import {model}"
        #     with open(viewsets_py_path, 'r') as f:
        #         lines = f.readlines()
        #     for i, line in enumerate(lines):
        #         if line.startswith('from ..models'):
        #             if model not in line:
        #                 merged_line = merge_item_into_import(line, model, 'from ..models')
        #                 lines[i] = merged_line
        #                 with open(viewsets_py_path, 'w') as f:
        #                     f.writelines(lines)
        #         else: 
        #             add_import(viewsets_py_path, model_import_line)

        # if serializer:
        #     serializer_import_line = f"from ..serializers import {serializer}"
        #     with open(viewsets_py_path, 'r') as f:
        #         lines = f.readlines()
       
        #     for i, line in enumerate(lines):
        #         if line.startswith('from ..serializers'):
        #             if serializer not in line:
        #                 merged_line = merge_item_into_import(line, serializer, 'from ..serializers')
        #                 lines[i] = merged_line
        #                 with open(viewsets_py_path, 'w') as f:
        #                     f.writelines(lines)
        #         else:    
        #             add_import(viewsets_py_path, serializer_import_line)



    #     # Render and inject the viewset content without imports
    #     template_no_import = templates_path / 'viewset_template_no_import.txt'
    #     content = render_template(
    #         template_no_import, 
    #         viewset_name=viewset_name,
    #         model_name=model_name,
    #         serializer_name=serializer_name
    #     )
    #     inject_element_into_file(viewsets_py_path, content)
    # else:
    #     # Create viewsets.py file with default content
    #     viewsets_py_path.write_text("# Django REST Framework Viewsets\n\n")
        
    #     # # Create viewsets folder and files
    #     # viewsets_folder_path.mkdir(parents=True, exist_ok=True)

    #     if path:
    #         custom_viewset_path = viewsets_folder_path / Path(path)
    #         custom_viewset_path.mkdir(parents=True, exist_ok=True)
    #     else:
    #         custom_viewset_path = viewsets_folder_path

    #     viewset_file_name = f"{snake_case(viewset_name)}.py"
    #     viewset_file_path = custom_viewset_path / viewset_file_name
    #     init_file_path = custom_viewset_path / '__init__.py'

    #     # Create the viewset file with full imports
    #     template = templates_path / 'viewset_template.txt'
    #     content = render_template(
    #         template,
    #         viewset_name=viewset_name,
    #         model_name=model_name,
    #         serializer_name=serializer_name
    #     )
    #     create_element_file(viewset_file_path, content)
    #     add_import_to_file(init_file_path, viewset_name, viewset_file_name)

    click.echo(f"Viewset '{viewset_name}' created successfully in app '{app_name}'.")
    return 0
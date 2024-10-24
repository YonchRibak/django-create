import os

def render_template(template_path, **kwargs):
    """
    Reads a template file and replaces placeholders with provided values.
    """
    with open(template_path, 'r') as file:
        content = file.read()

    # Replace placeholders in the content with the provided keyword arguments
    for key, value in kwargs.items():
        placeholder = f"{{{{ {key} }}}}"
        content = content.replace(placeholder, value)

    return content

def save_rendered_template(content, output_path):
    """
    Saves rendered template content to the specified output path.
    """
    with open(output_path, 'w') as file:
        file.write(content)

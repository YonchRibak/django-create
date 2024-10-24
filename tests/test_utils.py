import os
import pytest
from ..django_create.utils import (
    snake_case,
    render_template,
    save_rendered_template,
    inject_element_into_file,
    create_element_file,
    add_import_to_file
)

def test_snake_case():
    assert snake_case('CamelCase') == 'camel_case'
    assert snake_case('CamelCASE') == 'camel_case'
    assert snake_case('camelCase') == 'camel_case'
    assert snake_case('Already_Snake_Case') == 'already_snake_case'

def test_render_template(tmp_path):
    template_content = "class {{ model_name }}(models.Model):"
    template_path = tmp_path / "model_template.txt"
    template_path.write_text(template_content)

    result = render_template(str(template_path), model_name="TestModel")
    expected = "class TestModel(models.Model):"

    assert result == expected

def test_save_rendered_template(tmp_path):
    output_path = tmp_path / "output.txt"
    content = "This is a test."

    save_rendered_template(content, str(output_path))

    assert output_path.exists()
    assert output_path.read_text() == content

def test_inject_element_into_file(tmp_path):
    file_path = tmp_path / "models.py"
    file_path.write_text("class ExistingModel(models.Model):")

    element_content = "class NewModel(models.Model):"
    inject_element_into_file(str(file_path), element_content)

    assert file_path.read_text() == (
        "class ExistingModel(models.Model):\n\n\nclass NewModel(models.Model):"
    )

def test_create_element_file(tmp_path):
    element_path = tmp_path / "new_model.py"
    element_content = "class NewModel(models.Model):"

    create_element_file(str(element_path), element_content)

    assert element_path.exists()
    assert element_path.read_text() == element_content

def test_add_import_to_file(tmp_path):
    init_file_path = tmp_path / "__init__.py"
    element_name = "NewModel"
    element_file_name = "new_model.py"

    # Create an empty __init__.py file
    init_file_path.write_text("")

    add_import_to_file(str(init_file_path), element_name, element_file_name)

    expected_import = "from .new_model import NewModel\n"
    assert expected_import in init_file_path.read_text()

    # Test that it does not duplicate the import
    add_import_to_file(str(init_file_path), element_name, element_file_name)
    assert init_file_path.read_text().count(expected_import) == 1

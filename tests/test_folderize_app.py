import os
import pytest
from click.testing import CliRunner
from django_create.commands import folderize
from django_create.utils import create_mock_django_app, snake_case

def test_folderize_creates_folders_and_removes_files(tmp_path):
    # Create a mock Django app with models.py, views.py, and tests.py files
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True
    )
    
    # Ensure the files exist before running the command
    assert (app_path / 'models.py').exists()
    assert (app_path / 'views.py').exists()
    assert (app_path / 'tests.py').exists()

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)  # Change directory to ensure correct context for the command
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()


def test_folderize_aborts_if_app_does_not_exist(tmp_path):
    # Run the folderize command on a non-existent app
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'non_existent_app'})

    # Print output for debugging
    print(result.output)

    # Verify that the command aborts with an error message
    assert result.exit_code == 0
    assert "Error: The app 'non_existent_app' does not exist." in result.output

def test_folderize_works_with_empty_files(tmp_path):
    # Create a mock Django app with empty models.py, views.py, and tests.py files
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True
    )
    
    # Empty the content of each file
    (app_path / 'models.py').write_text("")
    (app_path / 'views.py').write_text("")
    (app_path / 'tests.py').write_text("")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()

def test_folderize_creates_folders_and_removes_files_in_subdirectory(tmp_path):
    # Create a mock Django app in a subdirectory with models.py, views.py, and tests.py files
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True,
        subdirectory='subdir'
    )
    
    # Ensure the files exist before running the command
    assert (app_path / 'models.py').exists()
    assert (app_path / 'views.py').exists()
    assert (app_path / 'tests.py').exists()

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)  # Change directory to ensure correct context for the command
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created in the subdirectory
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()


def test_folderize_aborts_if_app_in_subdirectory_does_not_exist(tmp_path):
    # Run the folderize command on a non-existent app in a subdirectory
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'non_existent_app'})

    # Print output for debugging
    print(result.output)

    # Verify that the command aborts with an error message
    assert result.exit_code == 0
    assert "Error: The app 'non_existent_app' does not exist." in result.output

def test_folderize_works_with_empty_files_in_subdirectory(tmp_path):
    # Create a mock Django app with empty models.py, views.py, and tests.py files in a subdirectory
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True,
        subdirectory='subdir'
    )
    
    # Empty the content of each file
    (app_path / 'models.py').write_text("")
    (app_path / 'views.py').write_text("")
    (app_path / 'tests.py').write_text("")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print output for debugging
    print(result.output)

    # Verify that the command executed successfully
    assert result.exit_code == 0
    assert "App 'testapp' has been folderized successfully." in result.output

    # Verify that the files have been removed and folders created in the subdirectory
    assert not (app_path / 'models.py').exists()
    assert not (app_path / 'views.py').exists()
    assert not (app_path / 'tests.py').exists()
    assert (app_path / 'models').is_dir()
    assert (app_path / 'views').is_dir()
    assert (app_path / 'tests').is_dir()
    assert (app_path / 'models' / '__init__.py').exists()
    assert (app_path / 'views' / '__init__.py').exists()
    assert (app_path / 'tests' / '__init__.py').exists()

def test_folderize_extracts_multiple_classes(tmp_path):
    # Create a mock Django app with all file types
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_tests_file=True,
        with_viewsets_file=True,
        with_serializers_file=True
    )

    # Define content for models.py
    models_content = """
from django.db import models
from django.utils import timezone

class ProductModel(models.Model):
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(default=timezone.now)

class OrderModel(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    
    class Meta:
        ordering = ['-created_at']

class UserProfileModel(models.Model):
    bio = models.TextField()
    avatar = models.ImageField(upload_to='avatars/')
"""

    # Define content for views.py
    views_content = """
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ProductModel, OrderModel

class ProductListView(LoginRequiredMixin, ListView):
    model = ProductModel
    template_name = 'products/list.html'
    context_object_name = 'products'

class OrderDetailView(DetailView):
    model = OrderModel
    template_name = 'orders/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Order Details'
        return context
"""

    # Define content for serializers.py
    serializers_content = """
from rest_framework import serializers
from .models import (
                    ProductModel, 
                    OrderModel, 
                    UserProfileModel 
                    )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['created_at']

class OrderSerializer(serializers.ModelSerializer):
    total_display = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderModel
        fields = ['id', 'total', 'status', 'total_display']
    
    def get_total_display(self, obj):
        return f"${obj.total:.2f}"

class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfileModel
        fields = ['id', 'bio', 'avatar', 'avatar_url']
    
    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None
"""

    # Define content for viewsets.py
    viewsets_content = """
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ProductModel, OrderModel
from .serializers import ProductSerializer, OrderSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer
"""

    # Define content for tests.py
    tests_content = """
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import ProductModel, OrderModel

class ProductModelTest(TestCase):
    def test_product_creation(self):
        product = ProductModel.objects.create(name='Test Product')
        self.assertIsNotNone(product.created_at)

class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.order = OrderModel.objects.create(
            total=99.99,
            status='pending'
        )

    def test_list_orders(self):
        response = self.client.get(reverse('order-list'))
        self.assertEqual(response.status_code, 200)
"""

    # Write content to files
    files_content = {
        'models.py': models_content,
        'views.py': views_content,
        'viewsets.py': viewsets_content,
        'serializers.py': serializers_content,
        'tests.py': tests_content
    }

    for file_name, content in files_content.items():
        file_path = app_path / file_name
        file_path.write_text(content)

    # Print initial state
    print("\nInitial state:")
    for file_name in files_content:
        file_path = app_path / file_name
        print(f"\n{file_name} exists: {file_path.exists()}")
        print(f"{file_name} content:\n{file_path.read_text()}")

    # Run the folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(
        folderize,
        obj={'app_name': 'testapp'},
        catch_exceptions=False
    )

    # Print command result details
    print("\nCommand execution:")
    print(f"Exit code: {result.exit_code}")
    print(f"Output:\n{result.output}")
    if result.exception:
        print(f"Exception: {result.exception}")
        import traceback
        traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)

    # Verify command execution
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}"
    assert "App 'testapp' has been folderized successfully." in result.output

    # Define expected files for each folder
    expected_files = {
        'models': {
            'product_model.py': ['ProductModel', 'models.Model'],
            'order_model.py': ['OrderModel', 'models.Model'],
            'user_profile_model.py': ['UserProfileModel', 'models.Model']
        },
        'views': {
            'product_list_view.py': ['ProductListView', 'ListView'],
            'order_detail_view.py': ['OrderDetailView', 'DetailView']
        },
        'serializers': {
            'product_serializer.py': ['ProductSerializer', 'serializers.ModelSerializer'],
            'order_serializer.py': ['OrderSerializer', 'serializers.ModelSerializer'],
            'user_profile_serializer.py': ['UserProfileSerializer', 'serializers.HyperlinkedModelSerializer']
        },
        'viewsets': {
            'product_viewset.py': ['ProductViewSet', 'viewsets.ModelViewSet'],
            'order_viewset.py': ['OrderViewSet', 'viewsets.ReadOnlyModelViewSet']
        },
        'tests': {
            'product_model_test.py': ['ProductModelTest', 'TestCase'],
            'order_viewset_test.py': ['OrderViewSetTest', 'APITestCase']
        }
    }

    # Verify each folder and its contents
    for folder_name, expected_files_dict in expected_files.items():
        folder_path = app_path / folder_name
        print(f"\nChecking {folder_name} folder:")
        
        # Check folder exists
        assert folder_path.exists(), f"{folder_name} folder should exist"
        
        # Check __init__.py exists
        init_file = folder_path / '__init__.py'
        assert init_file.exists(), f"Missing __init__.py in {folder_name}"
        init_content = init_file.read_text()
        
        # Check each expected file
        for file_name, expected_classes in expected_files_dict.items():
            if folder_name == "tests": 
                file_name = f'test_{file_name}'
            file_path = folder_path / file_name
            print(f"Checking {file_name}...")
            
            # Check file exists
            assert file_path.exists(), f"Missing file: {file_name}"
            content = file_path.read_text()
            print(f"Content:\n{content}")
            
            # Check for expected content
            for expected_class in expected_classes:
                assert expected_class in content, f"Missing {expected_class} in {file_name}"
            
            # Check import in __init__.py
            class_name = expected_classes[0]  # First item is the main class name
            expected_import = f"from .{file_name[:-3]} import {class_name}"
            assert expected_import in init_content, f"Missing import in {folder_name}/__init__.py: {expected_import}"

        # Additional checks for serializers
        if folder_name == 'serializers':
            for file_name in expected_files_dict:
                content = (folder_path / file_name).read_text()
                # Check for Meta class in serializers
                assert 'class Meta:' in content, f"Missing Meta class in {file_name}"
                # Check for proper model import
                assert 'from ..models import' in content, f"Missing model import in {file_name}"
                assert 'from .models import' not in content, f'Wrong import statement (.models) in {file_name}'

    # Verify original files are removed
    for file_name in files_content:
        original_file = app_path / file_name
        assert not original_file.exists(), f"Original {file_name} should be removed"

def test_folderize_handles_imports_correctly(tmp_path):
    """Test that folderize correctly updates imports when converting to folder structure."""
    # Create a mock Django app with various files containing imports
    app_path = create_mock_django_app(
        tmp_path,
        app_name='testapp',
        with_models_file=True,
        with_views_file=True,
        with_serializers_file=True,
        with_viewsets_file=True
    )

    # Define test content with various import styles and inline comments
    models_content = """from django.db import models
from django.utils import timezone

class UserModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

class ProfileModel(models.Model):  # User profile model
    bio = models.TextField()
    user = models.OneToOneField('UserModel', on_delete=models.CASCADE)
"""

    serializers_content = """from rest_framework import serializers
from .models import UserModel, ProfileModel  # Import models

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):  # Profile serializer
    class Meta:
        model = ProfileModel
        fields = ['bio', 'user']
"""

    viewsets_content = """from rest_framework import viewsets
from .models import UserModel
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
"""

    views_content = """from django.views import View
from django.shortcuts import render
from .models import UserModel, ProfileModel
from .serializers import UserSerializer  # For API views

class UserView(View):
    def get(self, request):
        users = UserModel.objects.all()
        return render(request, 'users.html', {'users': users})
"""

    # Write content to files
    (app_path / 'models.py').write_text(models_content)
    (app_path / 'serializers.py').write_text(serializers_content)
    (app_path / 'viewsets.py').write_text(viewsets_content)
    (app_path / 'views.py').write_text(views_content)

    # Run folderize command
    runner = CliRunner()
    os.chdir(tmp_path)
    result = runner.invoke(folderize, obj={'app_name': 'testapp'})

    # Print debug information
    print("\nCommand output:")
    print(result.output)
    if result.exception:
        import traceback
        traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)

    # Verify command execution
    assert result.exit_code == 0, f"Folderize command failed with exit code {result.exit_code}"

    # Check that original files were removed
    assert not (app_path / 'models.py').exists(), "models.py should be removed"
    assert not (app_path / 'serializers.py').exists(), "serializers.py should be removed"
    assert not (app_path / 'viewsets.py').exists(), "viewsets.py should be removed"
    assert not (app_path / 'views.py').exists(), "views.py should be removed"

    # Check that folders were created
    assert (app_path / 'models').is_dir(), "models folder should be created"
    assert (app_path / 'serializers').is_dir(), "serializers folder should be created"
    assert (app_path / 'viewsets').is_dir(), "viewsets folder should be created"
    assert (app_path / 'views').is_dir(), "views folder should be created"

    # Check model files
    user_model_file = app_path / 'models' / 'user_model.py'
    profile_model_file = app_path / 'models' / 'profile_model.py'
    
    user_model_content = user_model_file.read_text()
    profile_model_content = profile_model_file.read_text()
    
    # Verify Django imports are preserved
    assert "from django.db import models" in user_model_content, "Django imports should be preserved in UserModel"
    assert "from django.utils import timezone" in user_model_content, "Timezone import should be preserved in UserModel"
    
    # Verify comments are preserved
    assert "# User profile model" in profile_model_content, "Comments should be preserved in ProfileModel"

    # Check serializer files
    user_serializer_file = app_path / 'serializers' / 'user_serializer.py'
    profile_serializer_file = app_path / 'serializers' / 'profile_serializer.py'
    user_serializer_content = user_serializer_file.read_text()
    profile_serializer_content = profile_serializer_file.read_text()

    # Verify serializer imports and comments
    assert "from rest_framework import serializers" in user_serializer_content, "REST framework import should be preserved"
    assert "from ..models import" in user_serializer_content and "UserModel" in user_serializer_content, "Model import should use parent directory"
    assert "# Profile serializer" in profile_serializer_content, "Comments should be preserved in ProfileSerializer"
    assert "from ..models import" in profile_serializer_content and "ProfileModel" in profile_serializer_content, "Model import should use parent directory"

    # Check viewset files
    user_viewset_file = app_path / 'viewsets' / 'user_viewset.py'
    viewset_content = user_viewset_file.read_text()

    # Verify viewset imports
    assert "from rest_framework import viewsets" in viewset_content, "REST framework import should be preserved"
    assert "from ..models import UserModel" in viewset_content, "Model import should use parent directory"
    assert "from ..serializers import UserSerializer" in viewset_content, "Serializer import should use parent directory"

    # Check view files
    user_view_file = app_path / 'views' / 'user_view.py'
    view_content = user_view_file.read_text()

    # Verify view imports and comments
    assert "from django.views import View" in view_content, "Django import should be preserved"
    assert "from django.shortcuts import render" in view_content, "Django shortcuts import should be preserved"
    assert "from ..models import" in view_content and "UserModel" in view_content, "Model import should use parent directory"
    assert "from ..serializers import UserSerializer" in view_content, "Serializer import should use parent directory"
    assert "# For API views" in view_content, "Comments should be preserved"

    # Check __init__.py files
    models_init = (app_path / 'models' / '__init__.py').read_text()
    serializers_init = (app_path / 'serializers' / '__init__.py').read_text()
    viewsets_init = (app_path / 'viewsets' / '__init__.py').read_text()
    views_init = (app_path / 'views' / '__init__.py').read_text()

    # Verify init imports
    assert "from .user_model import UserModel" in models_init, "Model import should be in models/__init__.py"
    assert "from .profile_model import ProfileModel" in models_init, "Profile model import should be in models/__init__.py"
    assert "from .user_serializer import UserSerializer" in serializers_init, "Serializer import should be in serializers/__init__.py"
    assert "from .user_viewset import UserViewSet" in viewsets_init, "ViewSet import should be in viewsets/__init__.py"
    assert "from .user_view import UserView" in views_init, "View import should be in views/__init__.py"
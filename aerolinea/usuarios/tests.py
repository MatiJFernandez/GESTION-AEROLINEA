"""
Tests unitarios para la aplicación usuarios.

Este módulo contiene tests para:
- Modelo Usuario
- Vistas de autenticación
- Formularios
- Decoradores personalizados
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Usuario
from .forms import UsuarioRegistroForm, UsuarioPerfilForm
from .decorators import staff_required, role_required


class UsuarioModelTest(TestCase):
    """Tests para el modelo Usuario."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'rol': 'cliente',
            'telefono': '123456789'
        }
    
    def test_crear_usuario(self):
        """Test para crear un usuario básico."""
        user = Usuario.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name'],
            rol=self.user_data['rol'],
            telefono=self.user_data['telefono']
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.rol, 'cliente')
        self.assertEqual(user.get_full_name(), 'Test User')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_crear_superusuario(self):
        """Test para crear un superusuario."""
        admin_user = Usuario.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.rol, 'admin')
    
    def test_email_unico(self):
        """Test para verificar que el email debe ser único."""
        Usuario.objects.create_user(
            username='user1',
            email='test@example.com',
            password='pass123'
        )
        
        with self.assertRaises(IntegrityError):
            Usuario.objects.create_user(
                username='user2',
                email='test@example.com',
                password='pass123'
            )
    
    def test_rol_por_defecto(self):
        """Test para verificar que el rol por defecto es 'cliente'."""
        user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        self.assertEqual(user.rol, 'cliente')
    
    def test_str_representation(self):
        """Test para verificar la representación en string del modelo."""
        user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            first_name='Test',
            last_name='User'
        )
        
        self.assertEqual(str(user), 'Test User (testuser)')


class UsuarioFormTest(TestCase):
    """Tests para los formularios de usuario."""
    
    def test_usuario_registro_form_valido(self):
        """Test para un formulario de registro válido."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'telefono': '123456789'
        }
        
        form = UsuarioRegistroForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_usuario_registro_form_password_no_coincide(self):
        """Test para verificar que las contraseñas deben coincidir."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        form = UsuarioRegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_usuario_registro_form_email_duplicado(self):
        """Test para verificar que el email debe ser único."""
        # Crear usuario existente
        Usuario.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        form = UsuarioRegistroForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_usuario_perfil_form_valido(self):
        """Test para un formulario de perfil válido."""
        user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'telefono': '987654321'
        }
        
        form = UsuarioPerfilForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())


class UsuarioViewsTest(TestCase):
    """Tests para las vistas de usuario."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """Test para el GET de la vista de login."""
        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')
    
    def test_login_view_post_valido(self):
        """Test para el POST válido de la vista de login."""
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('vuelos:home'))
    
    def test_login_view_post_invalido(self):
        """Test para el POST inválido de la vista de login."""
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos')
    
    def test_registro_view_get(self):
        """Test para el GET de la vista de registro."""
        response = self.client.get(reverse('usuarios:registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/registro.html')
    
    def test_registro_view_post_valido(self):
        """Test para el POST válido de la vista de registro."""
        response = self.client.post(reverse('usuarios:registro'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'telefono': '123456789'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('vuelos:home'))
        
        # Verificar que el usuario fue creado
        user = Usuario.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.rol, 'cliente')
    
    def test_logout_view(self):
        """Test para la vista de logout."""
        # Login primero
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('usuarios:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que el usuario no está autenticado
        response = self.client.get(reverse('vuelos:home'))
        self.assertNotContains(response, 'testuser')
    
    def test_perfil_view_autenticado(self):
        """Test para la vista de perfil con usuario autenticado."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('usuarios:perfil'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/perfil.html')
    
    def test_perfil_view_no_autenticado(self):
        """Test para la vista de perfil sin usuario autenticado."""
        response = self.client.get(reverse('usuarios:perfil'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, reverse('usuarios:login') + '?next=' + reverse('usuarios:perfil'))


class UsuarioDecoratorsTest(TestCase):
    """Tests para los decoradores personalizados."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.staff_user = Usuario.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
    
    def test_staff_required_decorator_staff_user(self):
        """Test para decorador staff_required con usuario staff."""
        self.client.login(username='staffuser', password='staffpass123')
        
        # Crear una vista simple para testear
        from django.http import HttpResponse
        from django.urls import path
        
        @staff_required
        def test_view(request):
            return HttpResponse("Staff only")
        
        # Simular la llamada
        response = test_view(self.client.request)
        self.assertEqual(response.status_code, 200)
    
    def test_staff_required_decorator_normal_user(self):
        """Test para decorador staff_required con usuario normal."""
        self.client.login(username='testuser', password='testpass123')
        
        from django.http import HttpResponse
        
        @staff_required
        def test_view(request):
            return HttpResponse("Staff only")
        
        # Simular la llamada
        response = test_view(self.client.request)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_role_required_decorator(self):
        """Test para decorador role_required."""
        self.client.login(username='testuser', password='testpass123')
        
        from django.http import HttpResponse
        
        @role_required(['cliente'])
        def test_view(request):
            return HttpResponse("Cliente only")
        
        # Simular la llamada
        response = test_view(self.client.request)
        self.assertEqual(response.status_code, 200)
        
        @role_required(['admin'])
        def admin_view(request):
            return HttpResponse("Admin only")
        
        # Simular la llamada
        response = admin_view(self.client.request)
        self.assertEqual(response.status_code, 302)  # Redirect


class UsuarioIntegrationTest(TestCase):
    """Tests de integración para el flujo completo de usuario."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
    
    def test_flujo_completo_registro_login_logout(self):
        """Test para el flujo completo de registro, login y logout."""
        # 1. Registro
        response = self.client.post(reverse('usuarios:registro'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'telefono': '123456789'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 2. Login
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'newuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 3. Verificar acceso a página protegida
        response = self.client.get(reverse('usuarios:perfil'))
        self.assertEqual(response.status_code, 200)
        
        # 4. Logout
        response = self.client.get(reverse('usuarios:logout'))
        self.assertEqual(response.status_code, 302)
        
        # 5. Verificar que no puede acceder a página protegida
        response = self.client.get(reverse('usuarios:perfil'))
        self.assertEqual(response.status_code, 302)

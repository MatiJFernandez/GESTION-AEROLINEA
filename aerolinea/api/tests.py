"""
Tests para la API REST.

Este módulo contiene tests para los endpoints de la API.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from vuelos.models import Avion, Vuelo
from pasajeros.models import Pasajero
from reservas.models import Reserva

User = get_user_model()


class AutenticacionAPITests(TestCase):
    """Tests para la autenticación JWT."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        # Crear un usuario de prueba
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            rol='admin'
        )
    
    def test_obtener_token_jwt(self):
        """Test para obtener token JWT con credenciales válidas."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verificar datos del usuario en la respuesta
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@test.com')
    
    def test_token_invalidas_credenciales(self):
        """Test para verificar que se rechazan credenciales inválidas."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'password_incorrecta'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VuelosAPITests(TestCase):
    """Tests para los endpoints de vuelos."""
    
    def setUp(self):
        """Configuración inicial."""
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin'
        )
        
        # Crear datos de prueba
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=180,
            filas=30,
            columnas=6
        )
        
        self.vuelo = Vuelo.objects.create(
            avion=self.avion,
            origen='Buenos Aires',
            destino='Miami',
            estado='programado',
            precio_base=500.00
        )
    
    def test_listar_vuelos_sin_autenticacion(self):
        """Test que los vuelos son accesibles sin autenticación (read-only)."""
        url = reverse('vuelo-list')
        
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
    
    def test_listar_vuelos_con_filtro(self):
        """Test de filtrado de vuelos por origen."""
        url = reverse('vuelo-list')
        
        response = self.client.get(url, {'origen': 'Buenos Aires'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.data['results']:
            self.assertEqual(response.data['results'][0]['origen'], 'Buenos Aires')


class ReportesAPITests(TestCase):
    """Tests para los endpoints de reportes."""
    
    def setUp(self):
        """Configuración inicial."""
        self.client = APIClient()
        # Crear usuario admin
        self.usuario = User.objects.create_user(
            username='admin',
            password='admin123',
            rol='admin'
        )
    
    def test_acceso_reportes_sin_autenticacion(self):
        """Test que los reportes requieren autenticación."""
        url = '/api/reportes/estadisticas_generales/'
        
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_acceso_reportes_con_autenticacion(self):
        """Test acceso a reportes con usuario autenticado."""
        # Obtener token
        token_url = reverse('token_obtain_pair')
        token_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        token_response = self.client.post(token_url, token_data, format='json')
        token = token_response.data['access']
        
        # Hacer request autenticado
        url = '/api/reportes/estadisticas_generales/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        response = self.client.get(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_vuelos', response.data)
        self.assertIn('total_pasajeros', response.data)
        self.assertIn('total_reservas', response.data)


class PermisosAPITests(TestCase):
    """Tests para verificar permisos de acceso."""
    
    def setUp(self):
        """Configuración inicial."""
        self.client = APIClient()
    
    def test_usuario_cliente_no_puede_crear_vuelo(self):
        """Test que un cliente no puede crear vuelos."""
        # Crear usuario con rol cliente
        usuario_cliente = User.objects.create_user(
            username='cliente',
            password='cliente123',
            rol='cliente'
        )
        
        # Autenticar
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(
            token_url,
            {'username': 'cliente', 'password': 'cliente123'},
            format='json'
        )
        token = token_response.data['access']
        
        # Intentar crear vuelo
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        avion = Avion.objects.create(modelo='Test', capacidad=100, filas=10, columnas=10)
        
        url = reverse('vuelo-list')
        data = {
            'avion': avion.id,
            'origen': 'Test Origin',
            'destino': 'Test Destination',
            'estado': 'programado',
            'precio_base': 100.00
        }
        
        response = self.client.post(url, data, format='json')
        
        # Debería fallar porque el cliente no tiene permisos de admin
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])

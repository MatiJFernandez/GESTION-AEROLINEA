"""
Tests unitarios para la aplicación vuelos.

Este módulo contiene tests para:
- Modelos Vuelo, Avion, Asiento
- Vistas de vuelos
- Vistas administrativas
- Funcionalidades de búsqueda
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import json

from .models import Vuelo, Avion, Asiento
from usuarios.models import Usuario


class VueloModelTest(TestCase):
    """Tests para el modelo Vuelo."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=150,
            filas=25,
            columnas=6
        )
        
        self.fecha_salida = timezone.now() + timedelta(days=1)
        self.fecha_llegada = self.fecha_salida + timedelta(hours=2)
        
        self.vuelo = Vuelo.objects.create(
            avion=self.avion,
            origen='Buenos Aires',
            destino='Córdoba',
            fecha_salida=self.fecha_salida,
            fecha_llegada=self.fecha_llegada,
            duracion='2:00',
            estado='programado',
            precio_base=50000
        )
    
    def test_crear_vuelo(self):
        """Test para crear un vuelo básico."""
        self.assertEqual(self.vuelo.origen, 'Buenos Aires')
        self.assertEqual(self.vuelo.destino, 'Córdoba')
        self.assertEqual(self.vuelo.estado, 'programado')
        self.assertEqual(self.vuelo.precio_base, 50000)
        self.assertEqual(self.vuelo.avion, self.avion)
    
    def test_str_representation(self):
        """Test para verificar la representación en string del modelo."""
        expected = f"Vuelo {self.vuelo.id}: Buenos Aires → Córdoba"
        self.assertEqual(str(self.vuelo), expected)
    
    def test_get_estado_display(self):
        """Test para verificar los estados del vuelo."""
        self.assertEqual(self.vuelo.get_estado_display(), 'Programado')
        
        self.vuelo.estado = 'en_vuelo'
        self.assertEqual(self.vuelo.get_estado_display(), 'En Vuelo')
        
        self.vuelo.estado = 'aterrizado'
        self.assertEqual(self.vuelo.get_estado_display(), 'Aterrizado')
        
        self.vuelo.estado = 'cancelado'
        self.assertEqual(self.vuelo.get_estado_display(), 'Cancelado')
    
    def test_vuelo_futuro(self):
        """Test para verificar que un vuelo es futuro."""
        self.assertTrue(self.vuelo.es_futuro())
        
        # Vuelo pasado
        vuelo_pasado = Vuelo.objects.create(
            avion=self.avion,
            origen='Buenos Aires',
            destino='Córdoba',
            fecha_salida=timezone.now() - timedelta(days=1),
            fecha_llegada=timezone.now() - timedelta(hours=22),
            duracion='2:00',
            estado='aterrizado',
            precio_base=50000
        )
        
        self.assertFalse(vuelo_pasado.es_futuro())


class AvionModelTest(TestCase):
    """Tests para el modelo Avion."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=150,
            filas=25,
            columnas=6
        )
    
    def test_crear_avion(self):
        """Test para crear un avión básico."""
        self.assertEqual(self.avion.modelo, 'Boeing 737')
        self.assertEqual(self.avion.capacidad, 150)
        self.assertEqual(self.avion.filas, 25)
        self.assertEqual(self.avion.columnas, 6)
    
    def test_str_representation(self):
        """Test para verificar la representación en string del modelo."""
        self.assertEqual(str(self.avion), 'Boeing 737 (150 asientos)')
    
    def test_calcular_capacidad(self):
        """Test para verificar el cálculo de capacidad."""
        self.assertEqual(self.avion.calcular_capacidad(), 150)
        
        # Avión con diferentes dimensiones
        avion2 = Avion.objects.create(
            modelo='Airbus A320',
            capacidad=180,
            filas=30,
            columnas=6
        )
        
        self.assertEqual(avion2.calcular_capacidad(), 180)


class AsientoModelTest(TestCase):
    """Tests para el modelo Asiento."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=150,
            filas=25,
            columnas=6
        )
        
        self.asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
    
    def test_crear_asiento(self):
        """Test para crear un asiento básico."""
        self.assertEqual(self.asiento.numero, 'A1')
        self.assertEqual(self.asiento.fila, 1)
        self.assertEqual(self.asiento.columna, 'A')
        self.assertEqual(self.asiento.tipo, 'economica')
        self.assertEqual(self.asiento.estado, 'disponible')
        self.assertEqual(self.asiento.avion, self.avion)
    
    def test_str_representation(self):
        """Test para verificar la representación en string del modelo."""
        self.assertEqual(str(self.asiento), 'A1 (Boeing 737)')
    
    def test_get_tipo_display(self):
        """Test para verificar los tipos de asiento."""
        self.assertEqual(self.asiento.get_tipo_display(), 'Económica')
        
        self.asiento.tipo = 'premium'
        self.assertEqual(self.asiento.get_tipo_display(), 'Premium')
        
        self.asiento.tipo = 'primera'
        self.assertEqual(self.asiento.get_tipo_display(), 'Primera Clase')
    
    def test_get_estado_display(self):
        """Test para verificar los estados del asiento."""
        self.assertEqual(self.asiento.get_estado_display(), 'Disponible')
        
        self.asiento.estado = 'ocupado'
        self.assertEqual(self.asiento.get_estado_display(), 'Ocupado')
        
        self.asiento.estado = 'reservado'
        self.assertEqual(self.asiento.get_estado_display(), 'Reservado')
        
        self.asiento.estado = 'en_mantenimiento'
        self.assertEqual(self.asiento.get_estado_display(), 'En Mantenimiento')


class VueloViewsTest(TestCase):
    """Tests para las vistas de vuelos."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=150,
            filas=25,
            columnas=6
        )
        
        self.vuelo = Vuelo.objects.create(
            avion=self.avion,
            origen='Buenos Aires',
            destino='Córdoba',
            fecha_salida=timezone.now() + timedelta(days=1),
            fecha_llegada=timezone.now() + timedelta(days=1, hours=2),
            duracion='2:00',
            estado='programado',
            precio_base=50000
        )
    
    def test_home_view(self):
        """Test para la vista home."""
        response = self.client.get(reverse('vuelos:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vuelos/home.html')
    
    def test_lista_vuelos_view(self):
        """Test para la vista lista_vuelos."""
        response = self.client.get(reverse('vuelos:lista_vuelos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vuelos/lista_vuelos.html')
        self.assertContains(response, 'Buenos Aires')
        self.assertContains(response, 'Córdoba')
    
    def test_lista_vuelos_con_filtros(self):
        """Test para la vista lista_vuelos con filtros."""
        response = self.client.get(reverse('vuelos:lista_vuelos'), {
            'origen': 'Buenos Aires',
            'destino': 'Córdoba',
            'estado': 'programado'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buenos Aires')
        self.assertContains(response, 'Córdoba')
    
    def test_detalle_vuelo_view(self):
        """Test para la vista detalle_vuelo."""
        response = self.client.get(reverse('vuelos:detalle_vuelo', args=[self.vuelo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vuelos/detalle_vuelo.html')
        self.assertContains(response, 'Buenos Aires')
        self.assertContains(response, 'Córdoba')
    
    def test_detalle_vuelo_no_existe(self):
        """Test para la vista detalle_vuelo con vuelo inexistente."""
        response = self.client.get(reverse('vuelos:detalle_vuelo', args=[999]))
        self.assertEqual(response.status_code, 404)
    
    def test_buscar_vuelos_view_get(self):
        """Test para el GET de la vista buscar_vuelos."""
        response = self.client.get(reverse('vuelos:buscar_vuelos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'vuelos/buscar_vuelos.html')
    
    def test_buscar_vuelos_view_post(self):
        """Test para el POST de la vista buscar_vuelos."""
        response = self.client.post(reverse('vuelos:buscar_vuelos'), {
            'origen': 'Buenos Aires',
            'destino': 'Córdoba',
            'fecha_desde': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Buenos Aires')
        self.assertContains(response, 'Córdoba')
    
    def test_verificar_disponibilidad_view(self):
        """Test para la vista verificar_disponibilidad."""
        asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
        
        response = self.client.get(reverse('vuelos:verificar_disponibilidad', args=[asiento.id]), {
            'vuelo_id': self.vuelo.id
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('disponible', data)


class VueloAdminViewsTest(TestCase):
    """Tests para las vistas administrativas de vuelos."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.staff_user = Usuario.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=150,
            filas=25,
            columnas=6
        )
        
        self.vuelo = Vuelo.objects.create(
            avion=self.avion,
            origen='Buenos Aires',
            destino='Córdoba',
            fecha_salida=timezone.now() + timedelta(days=1),
            fecha_llegada=timezone.now() + timedelta(days=1, hours=2),
            duracion='2:00',
            estado='programado',
            precio_base=50000
        )
    
    def test_dashboard_admin_view_staff_user(self):
        """Test para dashboard_admin con usuario staff."""
        self.client.login(username='staffuser', password='staffpass123')
        
        response = self.client.get(reverse('vuelos:dashboard_admin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')
    
    def test_dashboard_admin_view_normal_user(self):
        """Test para dashboard_admin con usuario normal."""
        normal_user = Usuario.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpass123'
        )
        
        self.client.login(username='normaluser', password='normalpass123')
        
        response = self.client.get(reverse('vuelos:dashboard_admin'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_dashboard_admin_view_no_autenticado(self):
        """Test para dashboard_admin sin autenticación."""
        response = self.client.get(reverse('vuelos:dashboard_admin'))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_reporte_pasajeros_view_staff_user(self):
        """Test para reporte_pasajeros con usuario staff."""
        self.client.login(username='staffuser', password='staffpass123')
        
        response = self.client.get(reverse('vuelos:reporte_pasajeros'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/reporte_pasajeros.html')
    
    def test_estadisticas_ocupacion_view_staff_user(self):
        """Test para estadisticas_ocupacion con usuario staff."""
        self.client.login(username='staffuser', password='staffpass123')
        
        response = self.client.get(reverse('vuelos:estadisticas_ocupacion'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/estadisticas_ocupacion.html')
    
    def test_api_estadisticas_view_staff_user(self):
        """Test para api_estadisticas con usuario staff."""
        self.client.login(username='staffuser', password='staffpass123')
        
        response = self.client.get(reverse('vuelos:api_estadisticas'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('vuelos_hoy', data)
        self.assertIn('reservas_hoy', data)
        self.assertIn('ocupacion_porcentaje', data)
        self.assertIn('ingresos_hoy', data)


class VueloIntegrationTest(TestCase):
    """Tests de integración para el flujo completo de vuelos."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.avion = Avion.objects.create(
            modelo='Boeing 737',
            capacidad=150,
            filas=25,
            columnas=6
        )
        
        # Crear múltiples vuelos para testing
        for i in range(5):
            Vuelo.objects.create(
                avion=self.avion,
                origen=f'Ciudad {i}',
                destino=f'Destino {i}',
                fecha_salida=timezone.now() + timedelta(days=i+1),
                fecha_llegada=timezone.now() + timedelta(days=i+1, hours=2),
                duracion='2:00',
                estado='programado',
                precio_base=50000 + (i * 10000)
            )
    
    def test_flujo_completo_busqueda_vuelos(self):
        """Test para el flujo completo de búsqueda de vuelos."""
        # 1. Ir a la página de búsqueda
        response = self.client.get(reverse('vuelos:buscar_vuelos'))
        self.assertEqual(response.status_code, 200)
        
        # 2. Realizar búsqueda
        response = self.client.post(reverse('vuelos:buscar_vuelos'), {
            'origen': 'Ciudad 0',
            'destino': 'Destino 0'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ciudad 0')
        self.assertContains(response, 'Destino 0')
        
        # 3. Ver lista de vuelos
        response = self.client.get(reverse('vuelos:lista_vuelos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ciudad 0')
        
        # 4. Ver detalle de un vuelo
        vuelo = Vuelo.objects.first()
        response = self.client.get(reverse('vuelos:detalle_vuelo', args=[vuelo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, vuelo.origen)
        self.assertContains(response, vuelo.destino)
    
    def test_paginacion_lista_vuelos(self):
        """Test para verificar la paginación en lista_vuelos."""
        # Crear más vuelos para forzar paginación
        for i in range(15):
            Vuelo.objects.create(
                avion=self.avion,
                origen=f'Ciudad Pag {i}',
                destino=f'Destino Pag {i}',
                fecha_salida=timezone.now() + timedelta(days=i+10),
                fecha_llegada=timezone.now() + timedelta(days=i+10, hours=2),
                duracion='2:00',
                estado='programado',
                precio_base=50000
            )
        
        # Primera página
        response = self.client.get(reverse('vuelos:lista_vuelos'))
        self.assertEqual(response.status_code, 200)
        
        # Segunda página
        response = self.client.get(reverse('vuelos:lista_vuelos'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        
        # Página inexistente
        response = self.client.get(reverse('vuelos:lista_vuelos'), {'page': 999})
        self.assertEqual(response.status_code, 200)  # Debe mostrar la última página

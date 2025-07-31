"""
Tests unitarios para la aplicación reservas.

Este módulo contiene tests para:
- Modelos Reserva y Boleto
- Vistas de reservas
- Lógica de negocio
- Validaciones de reservas
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import datetime, timedelta
import uuid

from .models import Reserva, Boleto
from vuelos.models import Vuelo, Avion, Asiento
from pasajeros.models import Pasajero
from usuarios.models import Usuario


class ReservaModelTest(TestCase):
    """Tests para el modelo Reserva."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
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
        
        self.pasajero = Pasajero.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='12345678',
            email='juan@example.com',
            telefono='123456789',
            fecha_nacimiento='1990-01-01'
        )
        
        self.asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
        
        self.reserva = Reserva.objects.create(
            vuelo=self.vuelo,
            pasajero=self.pasajero,
            asiento=self.asiento,
            estado='pendiente',
            fecha_reserva=timezone.now(),
            precio=50000,
            codigo_reserva='RES-123456',
            fecha_vencimiento=timezone.now() + timedelta(hours=24)
        )
    
    def test_crear_reserva(self):
        """Test para crear una reserva básica."""
        self.assertEqual(self.reserva.vuelo, self.vuelo)
        self.assertEqual(self.reserva.pasajero, self.pasajero)
        self.assertEqual(self.reserva.asiento, self.asiento)
        self.assertEqual(self.reserva.estado, 'pendiente')
        self.assertEqual(self.reserva.precio, 50000)
        self.assertEqual(self.reserva.codigo_reserva, 'RES-123456')
    
    def test_str_representation(self):
        """Test para verificar la representación en string del modelo."""
        expected = f"Reserva {self.reserva.codigo_reserva} - {self.pasajero.get_nombre_completo()}"
        self.assertEqual(str(self.reserva), expected)
    
    def test_get_estado_display(self):
        """Test para verificar los estados de la reserva."""
        self.assertEqual(self.reserva.get_estado_display(), 'Pendiente')
        
        self.reserva.estado = 'confirmada'
        self.assertEqual(self.reserva.get_estado_display(), 'Confirmada')
        
        self.reserva.estado = 'cancelada'
        self.assertEqual(self.reserva.get_estado_display(), 'Cancelada')
    
    def test_reserva_expirada(self):
        """Test para verificar si una reserva está expirada."""
        # Reserva futura
        self.assertFalse(self.reserva.esta_expirada())
        
        # Reserva expirada
        reserva_expirada = Reserva.objects.create(
            vuelo=self.vuelo,
            pasajero=self.pasajero,
            asiento=self.asiento,
            estado='pendiente',
            fecha_reserva=timezone.now() - timedelta(days=2),
            precio=50000,
            codigo_reserva='RES-EXPIRED',
            fecha_vencimiento=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(reserva_expirada.esta_expirada())
    
    def test_generar_codigo_reserva(self):
        """Test para generar código único de reserva."""
        codigo = Reserva.generar_codigo_reserva()
        self.assertTrue(codigo.startswith('RES-'))
        self.assertEqual(len(codigo), 10)  # RES- + 6 caracteres
    
    def test_calcular_reembolso(self):
        """Test para calcular reembolso de reserva."""
        # Reserva confirmada reciente (100% reembolso)
        self.reserva.estado = 'confirmada'
        self.reserva.fecha_reserva = timezone.now() - timedelta(hours=1)
        
        reembolso = self.reserva.calcular_reembolso()
        self.assertEqual(reembolso, 50000)  # 100%
        
        # Reserva confirmada antigua (50% reembolso)
        self.reserva.fecha_reserva = timezone.now() - timedelta(days=2)
        reembolso = self.reserva.calcular_reembolso()
        self.assertEqual(reembolso, 25000)  # 50%
        
        # Reserva pendiente (100% reembolso)
        self.reserva.estado = 'pendiente'
        reembolso = self.reserva.calcular_reembolso()
        self.assertEqual(reembolso, 50000)  # 100%


class BoletoModelTest(TestCase):
    """Tests para el modelo Boleto."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
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
        
        self.pasajero = Pasajero.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='12345678',
            email='juan@example.com',
            telefono='123456789',
            fecha_nacimiento='1990-01-01'
        )
        
        self.asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
        
        self.reserva = Reserva.objects.create(
            vuelo=self.vuelo,
            pasajero=self.pasajero,
            asiento=self.asiento,
            estado='confirmada',
            fecha_reserva=timezone.now(),
            precio=50000,
            codigo_reserva='RES-123456',
            fecha_vencimiento=timezone.now() + timedelta(hours=24)
        )
        
        self.boleto = Boleto.objects.create(
            reserva=self.reserva,
            codigo_barra='BOL-123456',
            fecha_emision=timezone.now(),
            estado='emitido'
        )
    
    def test_crear_boleto(self):
        """Test para crear un boleto básico."""
        self.assertEqual(self.boleto.reserva, self.reserva)
        self.assertEqual(self.boleto.codigo_barra, 'BOL-123456')
        self.assertEqual(self.boleto.estado, 'emitido')
    
    def test_str_representation(self):
        """Test para verificar la representación en string del modelo."""
        expected = f"Boleto {self.boleto.codigo_barra} - {self.pasajero.get_nombre_completo()}"
        self.assertEqual(str(self.boleto), expected)
    
    def test_get_estado_display(self):
        """Test para verificar los estados del boleto."""
        self.assertEqual(self.boleto.get_estado_display(), 'Emitido')
        
        self.boleto.estado = 'utilizado'
        self.assertEqual(self.boleto.get_estado_display(), 'Utilizado')
        
        self.boleto.estado = 'cancelado'
        self.assertEqual(self.boleto.get_estado_display(), 'Cancelado')
    
    def test_generar_codigo_barra(self):
        """Test para generar código único de boleto."""
        codigo = Boleto.generar_codigo_barra()
        self.assertTrue(codigo.startswith('BOL-'))
        self.assertEqual(len(codigo), 14)  # BOL- + 10 caracteres


class ReservaViewsTest(TestCase):
    """Tests para las vistas de reservas."""
    
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
        
        self.pasajero = Pasajero.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='12345678',
            email='test@example.com',  # Mismo email que el usuario
            telefono='123456789',
            fecha_nacimiento='1990-01-01'
        )
        
        self.asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
        
        self.reserva = Reserva.objects.create(
            vuelo=self.vuelo,
            pasajero=self.pasajero,
            asiento=self.asiento,
            estado='pendiente',
            fecha_reserva=timezone.now(),
            precio=50000,
            codigo_reserva='RES-123456',
            fecha_vencimiento=timezone.now() + timedelta(hours=24)
        )
    
    def test_lista_reservas_view_autenticado(self):
        """Test para lista_reservas con usuario autenticado."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('reservas:lista_reservas'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/lista_reservas.html')
    
    def test_lista_reservas_view_no_autenticado(self):
        """Test para lista_reservas sin usuario autenticado."""
        response = self.client.get(reverse('reservas:lista_reservas'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_detalle_reserva_view_owner(self):
        """Test para detalle_reserva con propietario de la reserva."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('reservas:detalle_reserva', args=[self.reserva.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/detalle_reserva.html')
        self.assertContains(response, 'RES-123456')
    
    def test_detalle_reserva_view_not_owner(self):
        """Test para detalle_reserva con usuario que no es propietario."""
        other_user = Usuario.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        self.client.login(username='otheruser', password='otherpass123')
        
        response = self.client.get(reverse('reservas:detalle_reserva', args=[self.reserva.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_crear_reserva_view_get(self):
        """Test para el GET de crear_reserva."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('reservas:crear_reserva'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/crear_reserva.html')
    
    def test_confirmar_reserva_view_owner(self):
        """Test para confirmar_reserva con propietario de la reserva."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('reservas:confirmar_reserva', args=[self.reserva.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que la reserva fue confirmada
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.estado, 'confirmada')
        
        # Verificar que se creó el boleto
        self.assertTrue(hasattr(self.reserva, 'boleto'))
    
    def test_cancelar_reserva_view_owner(self):
        """Test para cancelar_reserva con propietario de la reserva."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('reservas:cancelar_reserva', args=[self.reserva.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que la reserva fue cancelada
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.estado, 'cancelada')
        
        # Verificar que el asiento fue liberado
        self.asiento.refresh_from_db()
        self.assertEqual(self.asiento.estado, 'disponible')
    
    def test_mi_historial_view_autenticado(self):
        """Test para mi_historial con usuario autenticado."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('reservas:mi_historial'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservas/mi_historial.html')
        self.assertContains(response, 'RES-123456')


class ReservaBusinessLogicTest(TestCase):
    """Tests para la lógica de negocio de reservas."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
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
        
        self.pasajero = Pasajero.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='12345678',
            email='juan@example.com',
            telefono='123456789',
            fecha_nacimiento='1990-01-01'
        )
        
        self.asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
    
    def test_verificar_disponibilidad_asiento(self):
        """Test para verificar disponibilidad de asiento."""
        # Asiento disponible
        self.assertTrue(self.asiento.estado == 'disponible')
        
        # Crear reserva
        reserva = Reserva.objects.create(
            vuelo=self.vuelo,
            pasajero=self.pasajero,
            asiento=self.asiento,
            estado='pendiente',
            fecha_reserva=timezone.now(),
            precio=50000,
            codigo_reserva='RES-123456',
            fecha_vencimiento=timezone.now() + timedelta(hours=24)
        )
        
        # Asiento ahora reservado
        self.asiento.refresh_from_db()
        self.assertEqual(self.asiento.estado, 'reservado')
        
        # Confirmar reserva
        reserva.estado = 'confirmada'
        reserva.save()
        
        # Asiento ahora ocupado
        self.asiento.refresh_from_db()
        self.assertEqual(self.asiento.estado, 'ocupado')
    
    def test_evitar_reserva_duplicada(self):
        """Test para evitar reservas duplicadas."""
        # Crear primera reserva
        Reserva.objects.create(
            vuelo=self.vuelo,
            pasajero=self.pasajero,
            asiento=self.asiento,
            estado='pendiente',
            fecha_reserva=timezone.now(),
            precio=50000,
            codigo_reserva='RES-123456',
            fecha_vencimiento=timezone.now() + timedelta(hours=24)
        )
        
        # Intentar crear segunda reserva para el mismo asiento
        with self.assertRaises(Exception):
            with transaction.atomic():
                Reserva.objects.create(
                    vuelo=self.vuelo,
                    pasajero=self.pasajero,
                    asiento=self.asiento,
                    estado='pendiente',
                    fecha_reserva=timezone.now(),
                    precio=50000,
                    codigo_reserva='RES-789012',
                    fecha_vencimiento=timezone.now() + timedelta(hours=24)
                )
    
    def test_codigo_reserva_unico(self):
        """Test para verificar que los códigos de reserva son únicos."""
        codigo1 = Reserva.generar_codigo_reserva()
        codigo2 = Reserva.generar_codigo_reserva()
        
        self.assertNotEqual(codigo1, codigo2)
        self.assertTrue(codigo1.startswith('RES-'))
        self.assertTrue(codigo2.startswith('RES-'))
    
    def test_calculo_precio_por_tipo_asiento(self):
        """Test para calcular precio según tipo de asiento."""
        # Asiento económico
        precio_economica = self.vuelo.calcular_precio_asiento('economica')
        self.assertEqual(precio_economica, 50000)
        
        # Asiento premium
        precio_premium = self.vuelo.calcular_precio_asiento('premium')
        self.assertEqual(precio_premium, 75000)  # 50% más
        
        # Asiento primera clase
        precio_primera = self.vuelo.calcular_precio_asiento('primera')
        self.assertEqual(precio_primera, 100000)  # 100% más


class ReservaIntegrationTest(TestCase):
    """Tests de integración para el flujo completo de reservas."""
    
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
        
        self.pasajero = Pasajero.objects.create(
            nombre='Juan',
            apellido='Pérez',
            documento='12345678',
            email='test@example.com',
            telefono='123456789',
            fecha_nacimiento='1990-01-01'
        )
        
        self.asiento = Asiento.objects.create(
            avion=self.avion,
            numero='A1',
            fila=1,
            columna='A',
            tipo='economica',
            estado='disponible'
        )
    
    def test_flujo_completo_reserva(self):
        """Test para el flujo completo de creación, confirmación y cancelación de reserva."""
        self.client.login(username='testuser', password='testpass123')
        
        # 1. Crear reserva
        response = self.client.post(reverse('reservas:crear_reserva'), {
            'vuelo': self.vuelo.id,
            'pasajero': self.pasajero.id,
            'asiento': self.asiento.id,
            'precio': 50000
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que se creó la reserva
        reserva = Reserva.objects.first()
        self.assertIsNotNone(reserva)
        self.assertEqual(reserva.estado, 'pendiente')
        
        # Verificar que el asiento está reservado
        self.asiento.refresh_from_db()
        self.assertEqual(self.asiento.estado, 'reservado')
        
        # 2. Confirmar reserva
        response = self.client.post(reverse('reservas:confirmar_reserva', args=[reserva.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la reserva fue confirmada
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'confirmada')
        
        # Verificar que se creó el boleto
        self.assertTrue(hasattr(reserva, 'boleto'))
        
        # Verificar que el asiento está ocupado
        self.asiento.refresh_from_db()
        self.assertEqual(self.asiento.estado, 'ocupado')
        
        # 3. Cancelar reserva
        response = self.client.post(reverse('reservas:cancelar_reserva', args=[reserva.id]))
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la reserva fue cancelada
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'cancelada')
        
        # Verificar que el asiento fue liberado
        self.asiento.refresh_from_db()
        self.assertEqual(self.asiento.estado, 'disponible')

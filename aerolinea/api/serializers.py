"""
Serializers de la aplicación API.

Este archivo contiene serializers que NO pertenecen a ninguna app específica:

- CustomTokenObtainPairSerializer: Serializer personalizado para JWT
  que incluye información del usuario en la respuesta del token

NOTA: Los serializers específicos de cada modelo están en sus respectivas apps:
- vuelos/serializers.py - Avion, Asiento, Vuelo
- pasajeros/serializers.py - Pasajero
- reservas/serializers.py - Reserva, Boleto
- usuarios/serializers.py - Usuario
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para la autenticación JWT.
    
    Extiende el TokenObtainPairSerializer de djangorestframework-simplejwt
    para incluir información adicional del usuario en la respuesta del token.
    
    Esta serialización es específica de la API y no pertenece a ninguna
    app de dominio (vuelos, pasajeros, reservas, usuarios).
    
    Returns:
        dict: Contiene 'access', 'refresh' y 'user' con información completa
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        # Agregar información adicional al token
        refresh = self.get_token(self.user)
        
        # Agregar claims personalizados al token
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Información del usuario
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'rol': self.user.rol,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        return data


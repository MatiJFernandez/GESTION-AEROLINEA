"""
Serializers para autenticación en la API.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para incluir información adicional en el token.
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


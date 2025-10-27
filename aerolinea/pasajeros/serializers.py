"""
Serializers para la aplicación pasajeros.

Este archivo define los serializers relacionados con:
- Pasajeros
"""

from rest_framework import serializers
from .models import Pasajero


class PasajeroSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Pasajero.
    """
    nombre_completo = serializers.SerializerMethodField()
    edad = serializers.IntegerField(source='get_edad', read_only=True)
    mayor_de_edad = serializers.BooleanField(source='es_mayor_de_edad', read_only=True)
    
    class Meta:
        model = Pasajero
        fields = '__all__'
        read_only_fields = ('id',)
        extra_kwargs = {
            'documento': {'validators': []},  # Eliminamos validación de único temporalmente
        }
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del pasajero."""
        return obj.get_nombre_completo()


class PasajeroListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar pasajeros.
    """
    nombre_completo = serializers.SerializerMethodField()
    edad = serializers.IntegerField(source='get_edad', read_only=True)
    
    class Meta:
        model = Pasajero
        fields = ['id', 'documento', 'nombre', 'apellido', 'nombre_completo',
                  'email', 'telefono', 'fecha_nacimiento', 'edad']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del pasajero."""
        return obj.get_nombre_completo()


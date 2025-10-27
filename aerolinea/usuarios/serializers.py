"""
Serializers para la aplicación usuarios.

Este archivo define los serializers relacionados con:
- Usuarios
"""

from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    """
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'rol', 'rol_display', 'telefono', 'is_active', 'is_staff',
                  'date_joined', 'last_login']
        read_only_fields = ('id', 'username', 'date_joined', 'last_login')


class UsuarioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar usuarios.
    """
    nombre_completo = serializers.SerializerMethodField()
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nombre_completo', 'email', 'rol',
                  'rol_display', 'is_active', 'date_joined']
    
    def get_nombre_completo(self, obj):
        """Retorna el nombre completo del usuario."""
        return obj.get_full_name()


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear usuarios.
    """
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'rol', 'telefono']
    
    def validate(self, attrs):
        """Valida que las contraseñas coincidan."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Las contraseñas no coinciden.",
                "password_confirm": "Las contraseñas no coinciden."
            })
        return attrs
    
    def create(self, validated_data):
        """Crea un nuevo usuario."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuarios.
    """
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email', 'telefono', 'rol']

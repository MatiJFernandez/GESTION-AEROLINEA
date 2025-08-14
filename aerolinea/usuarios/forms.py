"""
Formularios para la aplicación usuarios.

Este archivo contiene todos los formularios relacionados con:
- Registro de usuarios
- Edición de perfiles
- Inicio de sesión
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class UsuarioRegistroForm(UserCreationForm):
    """
    Formulario para el registro de nuevos usuarios.
    
    Extiende UserCreationForm de Django y agrega campos personalizados.
    """
    
    email = forms.EmailField(
        required=True,
        help_text='Ingrese una dirección de correo válida'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Ingrese su nombre'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Ingrese su apellido'
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        help_text='Ingrese su número de teléfono (opcional)'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'telefono', 
            'password1', 
            'password2'
        ]
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

class UsuarioPerfilForm(forms.ModelForm):
    """
    Formulario para editar el perfil de usuario.
    
    Permite editar información personal del usuario.
    """
    
    class Meta:
        model = Usuario
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'telefono'
        ]
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    """
    Formulario para el inicio de sesión.
    
    Campos básicos para autenticación de usuarios.
    """
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su nombre de usuario'
            }
        ),
        help_text='Ingrese su nombre de usuario'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su contraseña'
            }
        ),
        help_text='Ingrese su contraseña'
    )
    
    def clean(self):
        """Validación personalizada del formulario"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        if username and password:
            # Aquí podrías agregar validaciones adicionales si es necesario
            pass
        
        return cleaned_data 
"""
Formularios para la aplicación pasajeros.

Este archivo contiene todos los formularios relacionados con:
- Registro de pasajeros
- Edición de información de pasajeros
"""
import logging
from django import forms
from .models import Pasajero

logger = logging.getLogger(__name__)

class PasajeroForm(forms.ModelForm):
    """
    Formulario para crear y editar pasajeros.
    
    Incluye validaciones personalizadas para los datos del pasajero.
    """
    
    class Meta:
        model = Pasajero
        fields = [
            'nombre', 
            'apellido', 
            'documento', 
            'email', 
            'telefono', 
            'fecha_nacimiento', 
            'direccion'
        ]
        
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'documento': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_documento(self):
        """Validar que el documento sea único"""
        documento = self.cleaned_data.get('documento')
        if Pasajero.objects.filter(documento=documento).exists():
            raise forms.ValidationError('Este documento ya está registrado.')
        return documento
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        if Pasajero.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email 
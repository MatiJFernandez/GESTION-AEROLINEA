"""
Formularios para la aplicación reservas.

Este archivo contiene todos los formularios relacionados con:
- Creación de reservas
- Edición de reservas
"""

from django import forms
from .models import Reserva
from vuelos.models import Vuelo, Asiento
from pasajeros.models import Pasajero

class ReservaForm(forms.ModelForm):
    """
    Formulario para crear y editar reservas.
    
    Incluye validaciones para asegurar que la reserva sea válida.
    """
    
    class Meta:
        model = Reserva
        fields = [
            'vuelo', 
            'pasajero', 
            'asiento', 
            'precio', 
            'observaciones'
        ]
        
        widgets = {
            'vuelo': forms.Select(attrs={'class': 'form-control'}),
            'pasajero': forms.Select(attrs={'class': 'form-control'}),
            'asiento': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar vuelos programados
        self.fields['vuelo'].queryset = Vuelo.objects.filter(estado='programado')
        
        # Filtrar asientos disponibles
        self.fields['asiento'].queryset = Asiento.objects.filter(estado='disponible')
    
    def clean(self):
        """Validaciones personalizadas para la reserva"""
        cleaned_data = super().clean()
        vuelo = cleaned_data.get('vuelo')
        asiento = cleaned_data.get('asiento')
        pasajero = cleaned_data.get('pasajero')
        
        # Verificar que el asiento pertenezca al avión del vuelo
        if vuelo and asiento:
            if asiento.avion != vuelo.avion:
                raise forms.ValidationError(
                    'El asiento seleccionado no pertenece al avión del vuelo.'
                )
        
        # Verificar que el asiento esté disponible
        if asiento and asiento.estado != 'disponible':
            raise forms.ValidationError(
                'El asiento seleccionado no está disponible.'
            )
        
        # Verificar que no exista ya una reserva para este vuelo, pasajero y asiento
        if vuelo and pasajero and asiento:
            if Reserva.objects.filter(
                vuelo=vuelo, 
                pasajero=pasajero, 
                asiento=asiento
            ).exists():
                raise forms.ValidationError(
                    'Ya existe una reserva para este vuelo, pasajero y asiento.'
                )
        
        return cleaned_data 
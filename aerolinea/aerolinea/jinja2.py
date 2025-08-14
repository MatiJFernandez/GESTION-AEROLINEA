"""
Configuración de Jinja2 para el proyecto.

Este archivo configura el entorno de Jinja2 con filtros y funciones personalizadas.
"""

from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.translation import gettext as _


def environment(**options):
    """
    Configura el entorno de Jinja2.
    
    Args:
        **options: Opciones de configuración
        
    Returns:
        Environment: Entorno de Jinja2 configurado
    """
    env = Environment(**options)
    
    # Agregar funciones de Django
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
        '_': _,
    })
    
    # Agregar filtros personalizados
    env.filters.update({
        'currency': currency_filter,
        'date_format': date_format_filter,
        'truncate': truncate_filter,
    })
    
    return env


def currency_filter(value, currency='USD'):
    """
    Filtro para formatear moneda.
    
    Args:
        value: Valor a formatear
        currency: Moneda (USD, EUR, etc.)
        
    Returns:
        str: Valor formateado como moneda
    """
    if value is None:
        return ''
    
    try:
        value = float(value)
        if currency == 'USD':
            return f"${value:,.2f}"
        elif currency == 'EUR':
            return f"€{value:,.2f}"
        else:
            return f"{value:,.2f}"
    except (ValueError, TypeError):
        return str(value)


def date_format_filter(value, format='%d/%m/%Y'):
    """
    Filtro para formatear fechas.
    
    Args:
        value: Fecha a formatear
        format: Formato de fecha
        
    Returns:
        str: Fecha formateada
    """
    if value is None:
        return ''
    
    try:
        return value.strftime(format)
    except AttributeError:
        return str(value)


def truncate_filter(value, length=50):
    """
    Filtro para truncar texto.
    
    Args:
        value: Texto a truncar
        length: Longitud máxima
        
    Returns:
        str: Texto truncado
    """
    if value is None:
        return ''
    
    text = str(value)
    if len(text) <= length:
        return text
    
    return text[:length] + '...' 
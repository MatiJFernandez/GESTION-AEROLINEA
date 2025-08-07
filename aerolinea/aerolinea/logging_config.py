"""
Configuración de logging para el sistema de aerolínea.

Este módulo configura el sistema de logging para diferentes entornos
y tipos de mensajes (debug, info, warning, error).
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def configure_logging():
    """
    Configura el sistema de logging para la aplicación.
    
    Configura diferentes handlers para diferentes tipos de mensajes:
    - Console: Para desarrollo
    - File: Para producción y debugging
    - Email: Para errores críticos (opcional)
    """
    
    # Crear directorio de logs si no existe
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola (desarrollo)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler para archivo general
    general_handler = RotatingFileHandler(
        os.path.join(log_dir, 'aerolinea.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    general_handler.setLevel(logging.INFO)
    general_handler.setFormatter(formatter)
    
    # Handler para errores
    error_handler = RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler para debugging
    debug_handler = RotatingFileHandler(
        os.path.join(log_dir, 'debug.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=3
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(general_handler)
    root_logger.addHandler(error_handler)
    
    # Configurar loggers específicos
    loggers = {
        'django': {
            'handlers': ['console', 'general', 'error'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': False,
        },
        'vuelos': {
            'handlers': ['console', 'general', 'error', 'debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'reservas': {
            'handlers': ['console', 'general', 'error', 'debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'usuarios': {
            'handlers': ['console', 'general', 'error'],
            'level': 'INFO',
            'propagate': False,
        },
        'pasajeros': {
            'handlers': ['console', 'general', 'error'],
            'level': 'INFO',
            'propagate': False,
        },
    }
    
    # Aplicar configuración de loggers específicos
    for logger_name, logger_config in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, logger_config['level']))
        
        for handler_name in logger_config['handlers']:
            if handler_name == 'console':
                logger.addHandler(console_handler)
            elif handler_name == 'general':
                logger.addHandler(general_handler)
            elif handler_name == 'error':
                logger.addHandler(error_handler)
            elif handler_name == 'debug':
                logger.addHandler(debug_handler)
        
        logger.propagate = logger_config['propagate']


def log_user_action(user, action, details=None, level='info'):
    """
    Función helper para loggear acciones de usuarios.
    
    Args:
        user: Usuario que realiza la acción
        action: Descripción de la acción
        details: Detalles adicionales (opcional)
        level: Nivel de log (info, warning, error)
    """
    logger = logging.getLogger('usuarios')
    
    message = f"Usuario: {user.username} ({user.email}) - Acción: {action}"
    if details:
        message += f" - Detalles: {details}"
    
    if level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)


def log_reservation_action(reservation, action, user=None, details=None):
    """
    Función helper para loggear acciones relacionadas con reservas.
    
    Args:
        reservation: Objeto Reserva
        action: Descripción de la acción
        user: Usuario que realiza la acción (opcional)
        details: Detalles adicionales (opcional)
    """
    logger = logging.getLogger('reservas')
    
    user_info = f"Usuario: {user.username}" if user else "Sistema"
    message = f"{user_info} - Reserva: {reservation.codigo_reserva} - Acción: {action}"
    if details:
        message += f" - Detalles: {details}"
    
    logger.info(message)


def log_flight_action(flight, action, user=None, details=None):
    """
    Función helper para loggear acciones relacionadas con vuelos.
    
    Args:
        flight: Objeto Vuelo
        action: Descripción de la acción
        user: Usuario que realiza la acción (opcional)
        details: Detalles adicionales (opcional)
    """
    logger = logging.getLogger('vuelos')
    
    user_info = f"Usuario: {user.username}" if user else "Sistema"
    message = f"{user_info} - Vuelo: {flight.origen}→{flight.destino} - Acción: {action}"
    if details:
        message += f" - Detalles: {details}"
    
    logger.info(message) 
from django.apps import AppConfig


class VuelosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vuelos'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Importa los signals para que se registren.
        """
        import vuelos.signals

"""
URLs para la API REST.

Este archivo define las rutas de la API para los diferentes modelos.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from rest_framework_simplejwt.views import TokenObtainPairView as BaseTokenObtainPairView
from . import views
from .reports import ReportesViewSet
from .serializers import CustomTokenObtainPairSerializer


class TokenObtainPairView(BaseTokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Crear un router y registrar los viewsets
router = DefaultRouter()
router.register(r'aviones', views.AvionViewSet, basename='avion')
router.register(r'asientos', views.AsientoViewSet, basename='asiento')
router.register(r'vuelos', views.VueloViewSet, basename='vuelo')
router.register(r'pasajeros', views.PasajeroViewSet, basename='pasajero')
router.register(r'reservas', views.ReservaViewSet, basename='reserva')
router.register(r'boletos', views.BoletoViewSet, basename='boleto')
router.register(r'usuarios', views.UsuarioViewSet, basename='usuario')
router.register(r'reportes', ReportesViewSet, basename='reportes')

# Las URLs de la API
urlpatterns = [
    # Autenticación por token
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Endpoints de la API
    path('', include(router.urls)),
]


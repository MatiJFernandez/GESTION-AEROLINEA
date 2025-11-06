"""
URL configuration for aerolinea project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

# Swagger
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Sistema de Aerolínea API",
      default_version='v1',
      description="API REST para el sistema de gestión de aerolínea",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@aerolinea.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


# URLs principales del proyecto
urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Swagger documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API REST
    path('api/', include('api.urls')),
]

# URL para cambiar idioma (fuera de i18n_patterns para que funcione)
urlpatterns += [
    path('i18n/setlang/', set_language, name='set_language'),
]

# URLs con soporte para internacionalización
urlpatterns += i18n_patterns(
    # URLs de las aplicaciones del proyecto
    path('', include('vuelos.urls')),           # Página principal y gestión de vuelos
    path('usuarios/', include('usuarios.urls')), # Gestión de usuarios y autenticación
    path('pasajeros/', include('pasajeros.urls')), # Gestión de pasajeros
    path('reservas/', include('reservas.urls')), # Sistema de reservas
    prefix_default_language=True,
)



# Configuración para servir archivos estáticos y media en desarrollo
if settings.DEBUG:
    # Servir archivos estáticos (CSS, JS, imágenes)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Servir archivos de media (uploads)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 🛩️ Sistema de Aerolínea - Django

Sistema completo de gestión de aerolínea desarrollado en Django con funcionalidades avanzadas de reservas, gestión de vuelos, reportes administrativos y optimizaciones de rendimiento.

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd sistema-aerolinea
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   # Editar .env con tus configuraciones
   ```

5. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Poblar base de datos con datos de ejemplo**
   ```bash
   python manage.py poblar_datos
   ```

8. **Ejecutar el servidor**
   ```bash
   python manage.py runserver
   ```

### Endpoints Principales

#### Vuelos
- `GET /vuelos/` - Lista de vuelos
- `GET /vuelos/<id>/` - Detalle de vuelo
- `GET /vuelos/buscar/` - Búsqueda de vuelos


#### Reservas
- `GET /reservas/` - Lista de reservas
- `POST /reservas/crear/` - Crear reserva
- `POST /reservas/<id>/confirmar/` - Confirmar reserva
- `POST /reservas/<id>/cancelar/` - Cancelar reserva
- `GET /reservas/<codigo>/` - Buscar por código

#### Usuarios
- `GET /usuarios/login/` - Página de login
- `POST /usuarios/login/` - Autenticación
- `GET /usuarios/registro/` - Página de registro
- `POST /usuarios/registro/` - Crear usuario
- `GET /usuarios/perfil/` - Perfil de usuario

#### Administrativo
- `GET /vuelos/admin/dashboard/` - Dashboard administrativo
- `GET /vuelos/admin/reportes/pasajeros/` - Reporte de pasajeros
- `GET /vuelos/admin/estadisticas/ocupacion/` - Estadísticas de ocupación
- `GET /vuelos/admin/api/estadisticas/` - API de estadísticas

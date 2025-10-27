# API REST para Sistema de Aerolínea

Esta documentación describe el uso de la API REST implementada con Django REST Framework.

## Autenticación

La API utiliza autenticación por sesión y básica. Los permisos son:
- **IsAuthenticatedOrReadOnly**: Para vuelos, aviones y asientos (solo lectura para usuarios no autenticados)
- **IsAuthenticated**: Para pasajeros, reservas y boletos (requiere autenticación)
- **IsAuthenticated + IsAdminUser**: Para usuarios (solo admin)

## Endpoints Disponibles

### 1. Aviones (`/api/aviones/`)
- `GET /api/aviones/` - Lista todos los aviones
- `GET /api/aviones/{id}/` - Obtiene un avión específico
- `POST /api/aviones/` - Crea un nuevo avión
- `PUT /api/aviones/{id}/` - Actualiza un avión
- `DELETE /api/aviones/{id}/` - Elimina un avión

### 2. Asientos (`/api/asientos/`)
- `GET /api/asientos/` - Lista todos los asientos
- `GET /api/asientos/{id}/` - Obtiene un asiento específico
- `POST /api/asientos/` - Crea un nuevo asiento
- `PUT /api/asientos/{id}/` - Actualiza un asiento
- `DELETE /api/asientos/{id}/` - Elimina un asiento

**Filtros:**
- `GET /api/asientos/?avion=1` - Filtra por avión
- `GET /api/asientos/?estado=disponible` - Filtra por estado

### 3. Vuelos (`/api/vuelos/`)
- `GET /api/vuelos/` - Lista todos los vuelos
- `GET /api/vuelos/{id}/` - Obtiene un vuelo específico
- `POST /api/vuelos/` - Crea un nuevo vuelo
- `PUT /api/vuelos/{id}/` - Actualiza un vuelo
- `DELETE /api/vuelos/{id}/` - Elimina un vuelo

**Filtros:**
- `GET /api/vuelos/?origen=Buenos Aires` - Filtra por origen
- `GET /api/vuelos/?destino=Miami` - Filtra por destino
- `GET /api/vuelos/?estado=programado` - Filtra por estado
- `GET /api/vuelos/?fecha_min=2024-01-01` - Filtra por fecha mínima
- `GET /api/vuelos/?fecha_max=2024-12-31` - Filtra por fecha máxima

**Acciones personalizadas:**
- `GET /api/vuelos/{id}/asientos_disponibles/` - Obtiene asientos disponibles del vuelo

### 4. Pasajeros (`/api/pasajeros/`)
- `GET /api/pasajeros/` - Lista todos los pasajeros
- `GET /api/pasajeros/{id}/` - Obtiene un pasajero específico
- `POST /api/pasajeros/` - Crea un nuevo pasajero
- `PUT /api/pasajeros/{id}/` - Actualiza un pasajero
- `DELETE /api/pasajeros/{id}/` - Elimina un pasajero

**Filtros:**
- `GET /api/pasajeros/?documento=12345678` - Filtra por documento
- `GET /api/pasajeros/?nombre=Juan` - Filtra por nombre
- `GET /api/pasajeros/?apellido=Pérez` - Filtra por apellido

### 5. Reservas (`/api/reservas/`)
- `GET /api/reservas/` - Lista todas las reservas
- `GET /api/reservas/{id}/` - Obtiene una reserva específica
- `POST /api/reservas/` - Crea una nueva reserva
- `PUT /api/reservas/{id}/` - Actualiza una reserva
- `DELETE /api/reservas/{id}/` - Elimina una reserva

**Filtros:**
- `GET /api/reservas/?estado=confirmada` - Filtra por estado
- `GET /api/reservas/?pasajero=1` - Filtra por pasajero
- `GET /api/reservas/?vuelo=2` - Filtra por vuelo
- `GET /api/reservas/?codigo=ABC123` - Filtra por código

**Acciones personalizadas:**
- `POST /api/reservas/{id}/confirmar/` - Confirma una reserva pendiente
- `POST /api/reservas/{id}/cancelar/` - Cancela una reserva

### 6. Boletos (`/api/boletos/`)
- `GET /api/boletos/` - Lista todos los boletos
- `GET /api/boletos/{id}/` - Obtiene un boleto específico
- `POST /api/boletos/` - Crea un nuevo boleto
- `PUT /api/boletos/{id}/` - Actualiza un boleto
- `DELETE /api/boletos/{id}/` - Elimina un boleto

**Acciones personalizadas:**
- `POST /api/boletos/{id}/usar/` - Marca un boleto como usado

### 7. Usuarios (`/api/usuarios/`)
- `GET /api/usuarios/` - Lista todos los usuarios (solo admin)
- `GET /api/usuarios/{id}/` - Obtiene un usuario específico (solo admin)

## Paginación

Las respuestas de listado están paginadas con 20 elementos por página. Puedes navegar usando:
- `?page=1` - Primera página
- `?page=2` - Segunda página
- etc.

## Uso de la API

### Con curl

```bash
# Listar vuelos
curl http://localhost:8000/api/vuelos/

# Obtener un vuelo específico
curl http://localhost:8000/api/vuelos/1/

# Crear una reserva (requiere autenticación)
curl -X POST http://localhost:8000/api/reservas/ \
  -H "Content-Type: application/json" \
  -d '{
    "vuelo": 1,
    "pasajero": 1,
    "asiento": 5,
    "precio": 500.00,
    "fecha_vencimiento": "2024-12-31T23:59:59Z"
  }'
```

### Con el navegador

Puedes acceder directamente a `http://localhost:8000/api/` para ver la interfaz de exploración de la API proporcionada por DRF.

## Tipos de Respuesta

La API retorna datos en formato JSON con la siguiente estructura:

```json
{
  "id": 1,
  "campo1": "valor1",
  "campo2": "valor2",
  ...
}
```

Para listados paginados:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/vuelos/?page=2",
  "previous": null,
  "results": [...]
}
```

## Códigos de Estado HTTP

- `200 OK` - Petición exitosa
- `201 Created` - Recurso creado exitosamente
- `400 Bad Request` - Error en los datos enviados
- `401 Unauthorized` - No autenticado
- `403 Forbidden` - Sin permisos
- `404 Not Found` - Recurso no encontrado
- `500 Internal Server Error` - Error del servidor


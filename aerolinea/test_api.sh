#!/bin/bash

# Script para probar la API REST del Sistema de Aerolínea
# Autor: Sistema API
# Fecha: $(date +%Y-%m-%d)

echo "========================================="
echo "  Prueba de API REST - Sistema Aerolínea"
echo "========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# URL base
BASE_URL="http://localhost:8000/api"

# Obtener token
echo -e "${BLUE}1. Obteniendo token...${NC}"
TOKEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/token/" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access":"[^"]*' | sed 's/"access":"//')
REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"refresh":"[^"]*' | sed 's/"refresh":"//')

if [ -z "$ACCESS_TOKEN" ]; then
    echo -e "${RED}Error: No se pudo obtener el token${NC}"
    echo "Respuesta: $TOKEN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}✓ Token obtenido exitosamente${NC}"
echo ""

# Función para hacer requests
make_request() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    
    echo -e "${BLUE}Testing: ${method} ${endpoint}${NC}"
    
    if [ -n "$data" ]; then
        curl -s -X ${method} "${BASE_URL}${endpoint}" \
          -H "Authorization: Bearer ${ACCESS_TOKEN}" \
          -H "Content-Type: application/json" \
          -d "${data}" | python3 -m json.tool 2>/dev/null || echo "Respuesta: $(curl -s -X ${method} "${BASE_URL}${endpoint}" -H "Authorization: Bearer ${ACCESS_TOKEN}" -d "${data}")"
    else
        curl -s -X ${method} "${BASE_URL}${endpoint}" \
          -H "Authorization: Bearer ${ACCESS_TOKEN}" | python3 -m json.tool 2>/dev/null || echo "Respuesta: $(curl -s -X ${method} "${BASE_URL}${endpoint}" -H "Authorization: Bearer ${ACCESS_TOKEN}")"
    fi
    echo ""
}

# 2. Listar vuelos
echo -e "${BLUE}2. Listando vuelos...${NC}"
make_request "/vuelos/"

# 3. Estadísticas generales
echo -e "${BLUE}3. Obteniendo estadísticas generales...${NC}"
make_request "/reportes/estadisticas_generales/"

# 4. Reporte de vuelos
echo -e "${BLUE}4. Generando reporte de vuelos...${NC}"
make_request "/reportes/reporte_vuelos/"

# 5. Reporte de reservas
echo -e "${BLUE}5. Generando reporte de reservas...${NC}"
make_request "/reportes/reporte_reservas/"

# 6. Listar pasajeros
echo -e "${BLUE}6. Listando pasajeros...${NC}"
make_request "/pasajeros/"

# 7. Listar aviones
echo -e "${BLUE}7. Listando aviones...${NC}"
make_request "/aviones/"

# 8. Listar asientos
echo -e "${BLUE}8. Listando asientos...${NC}"
make_request "/asientos/"

# 9. Reporte de ocupación
echo -e "${BLUE}9. Generando reporte de ocupación...${NC}"
make_request "/reportes/reporte_ocupacion/"

# 10. Listar reservas
echo -e "${BLUE}10. Listando reservas...${NC}"
make_request "/reservas/"

echo "========================================="
echo -e "${GREEN}Pruebas completadas exitosamente${NC}"
echo "========================================="


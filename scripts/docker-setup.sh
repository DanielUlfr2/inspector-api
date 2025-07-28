#!/bin/bash

# Script de configuración de Docker para Inspector API
# Autor: Daniel Bermúdez
# Versión: 1.0.0
# Descripción: Script para configurar y ejecutar la aplicación en Docker

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Inspector API - Docker Setup${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Función para verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor, instala Docker primero."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado. Por favor, instala Docker Compose primero."
        exit 1
    fi
    
    print_message "Docker y Docker Compose están instalados correctamente."
}

# Función para crear certificados SSL auto-firmados
create_ssl_certificates() {
    if [ ! -d "ssl" ]; then
        print_message "Creando directorio SSL..."
        mkdir -p ssl
    fi
    
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_message "Generando certificados SSL auto-firmados..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/key.pem \
            -out ssl/cert.pem \
            -subj "/C=CO/ST=Colombia/L=Bogota/O=Inspector/CN=localhost"
        print_message "Certificados SSL generados correctamente."
    else
        print_message "Los certificados SSL ya existen."
    fi
}

# Función para crear archivos de inicialización de base de datos
create_db_init_files() {
    print_message "Creando archivos de inicialización de base de datos..."
    
    # Archivo para producción
    cat > init-db.sql << 'EOF'
-- Script de inicialización de base de datos para Inspector API
-- Autor: Daniel Bermúdez
-- Versión: 1.0.0

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear índices adicionales si es necesario
-- CREATE INDEX IF NOT EXISTS idx_registros_nombre ON registros(nombre);
-- CREATE INDEX IF NOT EXISTS idx_registros_numero_inspector ON registros(numero_inspector);

-- Insertar datos de prueba (opcional)
-- INSERT INTO usuarios (username, email, hashed_password, nombre, apellido, fecha_creacion) 
-- VALUES ('admin', 'admin@inspector.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8J8J8J8', 'Admin', 'Sistema', NOW())
-- ON CONFLICT (username) DO NOTHING;
EOF

    # Archivo para desarrollo
    cat > init-db-dev.sql << 'EOF'
-- Script de inicialización de base de datos para desarrollo
-- Autor: Daniel Bermúdez
-- Versión: 1.0.0

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear índices adicionales si es necesario
-- CREATE INDEX IF NOT EXISTS idx_registros_nombre ON registros(nombre);
-- CREATE INDEX IF NOT EXISTS idx_registros_numero_inspector ON registros(numero_inspector);

-- Insertar datos de prueba para desarrollo
INSERT INTO usuarios (username, email, hashed_password, nombre, apellido, fecha_creacion) 
VALUES ('admin', 'admin@inspector.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8J8J8J8', 'Admin', 'Sistema', NOW())
ON CONFLICT (username) DO NOTHING;
EOF

    print_message "Archivos de inicialización de base de datos creados."
}

# Función para crear directorio de logs
create_logs_directory() {
    if [ ! -d "logs" ]; then
        print_message "Creando directorio de logs..."
        mkdir -p logs
        touch logs/app.log
        touch logs/app_dev.log
        print_message "Directorio de logs creado."
    else
        print_message "El directorio de logs ya existe."
    fi
}

# Función para construir la imagen Docker
build_image() {
    print_message "Construyendo imagen Docker..."
    docker build -t inspector-api:latest .
    print_message "Imagen Docker construida correctamente."
}

# Función para ejecutar en modo desarrollo
run_development() {
    print_message "Iniciando servicios en modo desarrollo..."
    docker-compose -f docker-compose.dev.yml up -d
    
    print_message "Servicios iniciados:"
    echo "  - API: http://localhost:8000"
    echo "  - Documentación: http://localhost:8000/docs"
    echo "  - pgAdmin: http://localhost:8080 (admin@inspector.com / admin123)"
    echo "  - Base de datos: localhost:5433"
    echo "  - Redis: localhost:6380"
}

# Función para ejecutar en modo producción
run_production() {
    print_message "Iniciando servicios en modo producción..."
    docker-compose up -d
    
    print_message "Servicios iniciados:"
    echo "  - API: https://localhost"
    echo "  - Documentación: https://localhost/docs"
    echo "  - Base de datos: localhost:5432"
    echo "  - Redis: localhost:6379"
}

# Función para detener servicios
stop_services() {
    print_message "Deteniendo servicios..."
    docker-compose down
    docker-compose -f docker-compose.dev.yml down
    print_message "Servicios detenidos."
}

# Función para limpiar recursos
cleanup() {
    print_warning "¿Estás seguro de que quieres eliminar todos los contenedores, volúmenes e imágenes? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_message "Limpiando recursos Docker..."
        docker-compose down -v --rmi all
        docker-compose -f docker-compose.dev.yml down -v --rmi all
        docker system prune -f
        print_message "Limpieza completada."
    else
        print_message "Limpieza cancelada."
    fi
}

# Función para mostrar logs
show_logs() {
    print_message "Mostrando logs de la aplicación..."
    docker-compose logs -f api
}

# Función para mostrar logs de desarrollo
show_dev_logs() {
    print_message "Mostrando logs de la aplicación (desarrollo)..."
    docker-compose -f docker-compose.dev.yml logs -f api-dev
}

# Función para ejecutar migraciones
run_migrations() {
    print_message "Ejecutando migraciones de base de datos..."
    docker-compose exec api alembic upgrade head
    print_message "Migraciones ejecutadas correctamente."
}

# Función para ejecutar tests
run_tests() {
    print_message "Ejecutando tests..."
    docker-compose exec api python -m pytest tests/ -v
    print_message "Tests completados."
}

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  setup           Configurar el entorno Docker"
    echo "  dev             Ejecutar en modo desarrollo"
    echo "  prod            Ejecutar en modo producción"
    echo "  stop            Detener todos los servicios"
    echo "  logs            Mostrar logs de producción"
    echo "  logs-dev        Mostrar logs de desarrollo"
    echo "  migrate         Ejecutar migraciones"
    echo "  test            Ejecutar tests"
    echo "  cleanup         Limpiar recursos Docker"
    echo "  help            Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 setup        # Configurar entorno"
    echo "  $0 dev          # Ejecutar desarrollo"
    echo "  $0 prod         # Ejecutar producción"
}

# Función principal
main() {
    print_header
    
    case "${1:-help}" in
        setup)
            check_docker
            create_ssl_certificates
            create_db_init_files
            create_logs_directory
            build_image
            print_message "Configuración completada. Usa '$0 dev' o '$0 prod' para ejecutar."
            ;;
        dev)
            check_docker
            create_ssl_certificates
            create_db_init_files
            create_logs_directory
            run_development
            ;;
        prod)
            check_docker
            create_ssl_certificates
            create_db_init_files
            create_logs_directory
            build_image
            run_production
            ;;
        stop)
            stop_services
            ;;
        logs)
            show_logs
            ;;
        logs-dev)
            show_dev_logs
            ;;
        migrate)
            run_migrations
            ;;
        test)
            run_tests
            ;;
        cleanup)
            cleanup
            ;;
        help|*)
            show_help
            ;;
    esac
}

# Ejecutar función principal
main "$@" 
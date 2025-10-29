#!/usr/bin/env python3
"""
🧪 Script para ejecutar tests de integración - Inspector API

Este script ejecuta todos los tests de integración del proyecto,
incluyendo tests end-to-end, tests de servicios, y tests de base de datos.

Autor: Daniel Bermúdez
Versión: 1.0.0
"""

import subprocess
import sys
import os
from pathlib import Path


def run_integration_tests():
    """Ejecutar tests de integración"""
    print("🧪 Ejecutando tests de integración...")
    print("=" * 50)
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Comando para ejecutar tests de integración
    cmd = [
        "python", "-m", "pytest",
        "tests/test_integration.py",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-m", "integration"
    ]
    
    try:
        # Ejecutar tests
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Mostrar salida
        print("📋 Salida de los tests:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        # Mostrar resultado
        if result.returncode == 0:
            print("✅ Tests de integración completados exitosamente")
            print("📊 Reporte de cobertura generado en htmlcov/")
        else:
            print("❌ Tests de integración fallaron")
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ Error: pytest no encontrado. Instala las dependencias:")
        print("pip install pytest pytest-asyncio pytest-cov httpx")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        sys.exit(1)


def run_specific_integration_test(test_name):
    """Ejecutar un test de integración específico"""
    print(f"🧪 Ejecutando test específico: {test_name}")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    cmd = [
        "python", "-m", "pytest",
        f"tests/test_integration.py::{test_name}",
        "-v",
        "--tb=short",
        "-m", "integration"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📋 Salida del test:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Test específico completado exitosamente")
        else:
            print("❌ Test específico falló")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error ejecutando test específico: {e}")
        sys.exit(1)


def show_available_tests():
    """Mostrar tests de integración disponibles"""
    print("📋 Tests de integración disponibles:")
    print("=" * 50)
    
    integration_tests = [
        "TestIntegrationAuth.test_complete_auth_flow",
        "TestIntegrationAuth.test_auth_with_invalid_credentials",
        "TestIntegrationAuth.test_protected_endpoints_without_auth",
        "TestIntegrationRegistros.test_complete_registro_lifecycle",
        "TestIntegrationRegistros.test_registros_with_complex_filters",
        "TestIntegrationRegistros.test_registros_pagination",
        "TestIntegrationRegistros.test_registros_validation_errors",
        "TestIntegrationServices.test_auth_service_integration",
        "TestIntegrationServices.test_registro_service_integration",
        "TestIntegrationDatabase.test_database_connection",
        "TestIntegrationDatabase.test_database_constraints",
        "TestIntegrationAPI.test_api_health_check",
        "TestIntegrationAPI.test_api_documentation",
        "TestIntegrationAPI.test_api_cors"
    ]
    
    for i, test in enumerate(integration_tests, 1):
        print(f"{i:2d}. {test}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            show_available_tests()
        elif sys.argv[1] == "--test":
            if len(sys.argv) > 2:
                run_specific_integration_test(sys.argv[2])
            else:
                print("❌ Error: Debes especificar el nombre del test")
                print("Uso: python scripts/run_integration_tests.py --test TestName")
        else:
            print("❌ Error: Argumento no válido")
            print("Uso:")
            print("  python scripts/run_integration_tests.py          # Ejecutar todos")
            print("  python scripts/run_integration_tests.py --list   # Listar tests")
            print("  python scripts/run_integration_tests.py --test TestName  # Test específico")
    else:
        run_integration_tests()
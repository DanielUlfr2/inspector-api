#!/usr/bin/env python3
"""
Script para ejecutar tests de Inspector API
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    print(f"Comando: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Comando ejecutado exitosamente")
        if result.stdout:
            print("Salida:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando comando: {e}")
        if e.stdout:
            print("Salida estándar:")
            print(e.stdout)
        if e.stderr:
            print("Error estándar:")
            print(e.stderr)
        return False


def main():
    """Función principal del script"""
    print("🧪 SISTEMA DE TESTS - INSPECTOR API")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("app").exists():
        print("❌ Error: No se encontró el directorio 'app'")
        print("   Ejecuta este script desde la raíz del proyecto")
        sys.exit(1)
    
    # Verificar que existe el directorio de tests
    if not Path("tests").exists():
        print("❌ Error: No se encontró el directorio 'tests'")
        sys.exit(1)
    
    # Opciones disponibles
    print("\n📋 Opciones disponibles:")
    print("1. Tests unitarios básicos")
    print("2. Tests de autenticación")
    print("3. Tests de CRUD")
    print("4. Tests de validación")
    print("5. Todos los tests")
    print("6. Tests con coverage")
    print("7. Tests rápidos (sin coverage)")
    print("8. Limpiar archivos de coverage")
    
    try:
        choice = input("\nSelecciona una opción (1-8): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
        sys.exit(0)
    
    commands = {
        "1": "pytest tests/ -m unit -v",
        "2": "pytest tests/test_auth.py -v",
        "3": "pytest tests/test_registros.py -v",
        "4": "pytest tests/test_schemas.py -v",
        "5": "pytest tests/ -v",
        "6": "pytest tests/ --cov=app --cov-report=html --cov-report=term-missing -v",
        "7": "pytest tests/ --no-cov -v",
        "8": "rm -rf htmlcov/ .coverage coverage.xml"
    }
    
    descriptions = {
        "1": "Ejecutando tests unitarios básicos...",
        "2": "Ejecutando tests de autenticación...",
        "3": "Ejecutando tests de CRUD...",
        "4": "Ejecutando tests de validación...",
        "5": "Ejecutando todos los tests...",
        "6": "Ejecutando tests con coverage...",
        "7": "Ejecutando tests rápidos...",
        "8": "Limpiando archivos de coverage..."
    }
    
    if choice in commands:
        success = run_command(commands[choice], descriptions[choice])
        
        if success and choice == "6":
            print("\n📊 Reporte de coverage generado en htmlcov/index.html")
            print("   Abre el archivo en tu navegador para ver el reporte detallado")
        
        if success and choice in ["1", "2", "3", "4", "5", "6", "7"]:
            print("\n✅ Tests completados")
        elif success and choice == "8":
            print("\n✅ Archivos de coverage limpiados")
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main() 
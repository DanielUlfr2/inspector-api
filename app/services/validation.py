import re
import logging
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Registro

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    
    def __init__(self, message: str, details: Optional[Dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

def extract_inspector_number_from_name(nombre: str, numero_inspector: int) -> Optional[int]:
    """
    Extrae el número de inspector del nombre basándose en el patrón 'ins' + dígitos.
    El número extraído debe coincidir exactamente con el numero_inspector proporcionado.
    """
    if not nombre or not numero_inspector:
        return None
    
    # Buscar el patrón 'ins' seguido del número exacto
    # Usar lookahead negativo para evitar coincidencias parciales
    pattern = rf'ins{numero_inspector}(?!\d)'
    
    logger.warning(f"[EXTRACCIÓN] Buscando patrón exacto '{pattern}' en nombre '{nombre}' para numero_inspector={numero_inspector}")
    
    match = re.search(pattern, nombre, re.IGNORECASE)
    if match:
        logger.warning(f"[EXTRACCIÓN] OK Encontrado patrón exacto: '{match.group(0)}' en posición {match.start()}-{match.end()}")
        return numero_inspector
    
    # Si no se encontró con el patrón exacto, intentar con patrones más flexibles
    # Para números de un dígito (1-9), buscar ins01, ins02, etc.
    if numero_inspector in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        # Buscar ins + 2 dígitos donde el segundo dígito sea el número
        pattern_flexible = rf'ins0{numero_inspector}(?!\d)'
        logger.warning(f"[EXTRACCIÓN] Intentando patrón flexible '{pattern_flexible}' para número de un dígito")
        
        match = re.search(pattern_flexible, nombre, re.IGNORECASE)
        if match:
            logger.warning(f"[EXTRACCIÓN] OK Encontrado con patrón flexible: '{match.group(0)}' -> {numero_inspector}")
            return numero_inspector
    
    # Si no se encontró, buscar cualquier patrón 'ins' + dígitos para debugging
    all_matches = re.findall(r'ins(\d+)', nombre, re.IGNORECASE)
    if all_matches:
        logger.warning(f"[EXTRACCIÓN] DEBUG Encontrados patrones 'ins' en '{nombre}': {all_matches}")
    
    logger.warning(f"[EXTRACCIÓN] ERROR No se encontró ningún patrón válido en '{nombre}' para numero_inspector={numero_inspector}")
    return None

def validate_inspector_number_format(numero_inspector: int) -> Tuple[bool, int]:
    """
    Valida que el numero_inspector tenga al menos 2 caracteres numéricos.
    Si tiene solo 1 dígito (1-9), automáticamente agrega un cero a la izquierda.
    Retorna (es_válido, numero_corregido)
    """
    numero_str = str(numero_inspector)
    
    # Si tiene solo 1 dígito y está entre 1-9, agregar cero a la izquierda
    if len(numero_str) == 1 and numero_inspector in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        numero_corregido = int(f"0{numero_str}")
        logger.info(f"AUTO-CORRECCIÓN: Número de inspector '{numero_inspector}' corregido a '{numero_corregido}' (agregado cero a la izquierda)")
        return True, numero_corregido
    
    # Si tiene menos de 2 dígitos pero no es 1-9, es inválido
    if len(numero_str) < 2:
        logger.warning(f"VALIDACIÓN FALLIDA: El número de inspector '{numero_inspector}' tiene solo {len(numero_str)} caracteres. Se requieren al menos 2 caracteres numéricos.")
        return False, numero_inspector
    
    return True, numero_inspector

def validate_inspector_number_match(numero_inspector: int, nombre: str) -> Tuple[bool, int]:
    """
    Valida que el numero_inspector coincida exactamente con el número extraído del nombre
    después del prefijo 'ins'.
    Retorna (es_válido, numero_corregido)
    """
    # Primero validar el formato del número (mínimo 2 dígitos) y aplicar auto-corrección
    is_valid_format, numero_corregido = validate_inspector_number_format(numero_inspector)
    if not is_valid_format:
        return False, numero_inspector
    
    extracted_number = extract_inspector_number_from_name(nombre, numero_corregido)
    if extracted_number is None:
        logger.warning(
            f"[VALIDACIÓN] WARNING No se pudo extraer un número de inspector del nombre: '{nombre}'. "
            f"El nombre debe contener el patrón 'ins' seguido de exactamente {len(str(numero_corregido))} dígitos "
            f"(ej: para numero_inspector={numero_corregido}, debe ser 'ins{numero_corregido}')."
        )
        return False, numero_corregido
    
    is_valid = numero_corregido == extracted_number
    if is_valid:
        logger.info(
            f"[VALIDACIÓN] OK Coincidencia exitosa: numero_inspector={numero_corregido} coincide con "
            f"el número extraído del nombre '{nombre}' (extraído: {extracted_number})"
        )
    else:
        logger.warning(
            f"[VALIDACIÓN] ERROR Inconsistencia detectada: El número de inspector '{numero_corregido}' no coincide "
            f"con el número extraído del nombre '{nombre}' (número extraído: {extracted_number}). "
            f"El nombre debe contener exactamente 'ins{numero_corregido}' (buscando {len(str(numero_corregido))} dígitos)."
        )
    
    return is_valid, numero_corregido

async def check_duplicate_inspector_number(
    session: AsyncSession, 
    numero_inspector: int, 
    exclude_id: Optional[int] = None
) -> bool:
    """
    Verifica si ya existe un registro con el mismo numero_inspector.
    """
    query = select(Registro).where(Registro.numero_inspector == numero_inspector)
    if exclude_id:
        query = query.where(Registro.id != exclude_id)
    
    result = await session.execute(query)
    existing_records = result.scalars().all()
    
    if existing_records:
        # Log todos los registros duplicados encontrados
        for record in existing_records:
            logger.warning(
                f"[DUPLICADO] ERROR Ya existe un registro en la base de datos con numero_inspector={numero_inspector} "
                f"(ID={record.id}, Nombre='{record.nombre}'). "
                f"El número de inspector debe ser único."
            )
        return True
    
    return False

async def check_duplicate_nombre(
    session: AsyncSession, 
    nombre: str, 
    numero_inspector: int = None,
    exclude_id: Optional[int] = None
) -> bool:
    """
    Verifica si ya existe un registro con el mismo nombre Y numero_inspector.
    Los duplicados solo se consideran cuando ambas columnas coincidan.
    """
    query = select(Registro).where(Registro.nombre == nombre)
    
    # Solo validar duplicados si también tenemos numero_inspector
    if numero_inspector is not None:
        query = query.where(Registro.numero_inspector == numero_inspector)
    
    if exclude_id:
        query = query.where(Registro.id != exclude_id)
    
    result = await session.execute(query)
    existing_records = result.scalars().all()
    
    if existing_records:
        # Log todos los registros duplicados encontrados
        for record in existing_records:
            if numero_inspector is not None:
                logger.warning(
                    f"[DUPLICADO] ERROR Ya existe un registro en la base de datos con nombre='{nombre}' Y numero_inspector={numero_inspector} "
                    f"(ID={record.id}). "
                    f"La combinación de nombre y número de inspector debe ser única."
                )
            else:
                logger.warning(
                    f"[DUPLICADO] ERROR Ya existe un registro en la base de datos con nombre='{nombre}' "
                    f"(ID={record.id}, numero_inspector={record.numero_inspector}). "
                    f"El nombre debe ser único."
                )
        return True
    
    return False

async def validate_single_registro(
    session: AsyncSession, 
    registro_data: Dict, 
    exclude_id: Optional[int] = None
) -> Tuple[bool, List[str], List[str]]:
    """
    Valida un registro individual según todas las reglas.
    Retorna (es_válido, lista_de_errores, tipos_de_error)
    """
    errors = []
    tipos_error = []
    
    # Validar coincidencia numero_inspector con nombre
    numero_inspector = registro_data.get('numero_inspector')
    nombre = registro_data.get('nombre')
    
    if numero_inspector is not None:
        # Validar formato del número de inspector y aplicar auto-corrección
        is_valid_format, numero_corregido = validate_inspector_number_format(numero_inspector)
        if not is_valid_format:
            errors.append(
                f"ERROR El número de inspector '{numero_inspector}' debe tener al menos 2 caracteres numéricos (actualmente tiene {len(str(numero_inspector))})"
            )
            tipos_error.append("formato_numero_inspector")
        elif nombre:
            is_valid_match, numero_final = validate_inspector_number_match(numero_inspector, nombre)
            if not is_valid_match:
                errors.append(
                    f"ERROR El número de inspector '{numero_final}' no coincide con el número "
                    f"extraído del nombre '{nombre}'. El nombre debe contener 'ins{numero_final}'"
                )
                tipos_error.append("coincidencia_numero_nombre")
            else:
                # Si la validación es exitosa, actualizar el número corregido en los datos
                registro_data['numero_inspector'] = numero_final
    
    # Validar campos por tipo de contenido
    # Campos requeridos
    campos_requeridos = ['nombre', 'status']
    for campo in campos_requeridos:
        valor = registro_data.get(campo, '')
        es_valido, mensaje = validate_campo_requerido(valor, campo)
        if not es_valido:
            errors.append(f"ERROR {mensaje}")
            tipos_error.append("campo_requerido")
    
    # Validar celular (numérico, exactamente 10 dígitos)
    celular = registro_data.get('celular', '')
    es_valido, mensaje = validate_celular(celular)
    if not es_valido:
        errors.append(f"ERROR {mensaje}")
        tipos_error.append("formato_celular")
    
    # Validar correo (formato de email válido)
    correo = registro_data.get('correo', '')
    es_valido, mensaje = validate_correo(correo)
    if not es_valido:
        errors.append(f"ERROR {mensaje}")
        tipos_error.append("formato_correo")
    
    # Validar campos de texto (no vacíos, sin caracteres especiales problemáticos)
    campos_texto = ['nombre', 'status', 'zona', 'supervisor']
    for campo in campos_texto:
        valor = registro_data.get(campo, '')
        if valor:  # Solo validar si no está vacío
            es_valido, mensaje = validate_campo_texto(valor, campo)
            if not es_valido:
                errors.append(f"ERROR {mensaje}")
                tipos_error.append("formato_texto")
    
    # Validar duplicados en base de datos
    if nombre:
        # Verificar duplicados de nombre + numero_inspector
        is_duplicate = await check_duplicate_nombre(session, nombre, numero_inspector, exclude_id)
        if is_duplicate:
            errors.append(
                f"ERROR Ya existe un registro con nombre='{nombre}' y numero_inspector={numero_inspector}. "
                f"La combinación de nombre y número de inspector debe ser única."
            )
            tipos_error.append("duplicado_nombre_numero")
    
    if numero_inspector:
        # Verificar duplicados de numero_inspector
        is_duplicate = await check_duplicate_inspector_number(session, numero_inspector, exclude_id)
        if is_duplicate:
            errors.append(
                f"ERROR Ya existe un registro con numero_inspector={numero_inspector}. "
                f"El número de inspector debe ser único."
            )
            tipos_error.append("duplicado_numero_inspector")
    
    return len(errors) == 0, errors, tipos_error

async def validate_bulk_registros(
    session: AsyncSession, 
    registros_data: List[Dict]
) -> Tuple[List[Dict], List[Dict]]:
    """
    Valida una lista de registros y retorna los válidos e inválidos.
    Retorna (registros_válidos, registros_inválidos_con_errores)
    """
    registros_validos = []
    registros_invalidos = []
    
    logger.info(f"[VALIDACIÓN MASIVA] Iniciando validación de {len(registros_data)} registros")
    
    for i, registro_data in enumerate(registros_data, 1):
        logger.debug(f"[VALIDACIÓN MASIVA] Procesando registro {i}/{len(registros_data)}: {registro_data.get('nombre', 'SIN NOMBRE')}")
        
        try:
            is_valid, errors, tipos_error = await validate_single_registro(session, registro_data)
            
            if is_valid:
                registros_validos.append(registro_data)
                logger.debug(f"[VALIDACIÓN MASIVA] OK Registro {i} válido: {registro_data.get('nombre', 'SIN NOMBRE')}")
            else:
                error_info = {
                    'registro': registro_data,
                    'errors': errors,
                    'tipos_error': tipos_error,
                    'row_number': i
                }
                registros_invalidos.append(error_info)
                logger.warning(
                    f"[VALIDACIÓN MASIVA] ERROR Registro {i} inválido: {registro_data.get('nombre', 'SIN NOMBRE')} - "
                    f"Errores: {len(errors)}"
                )
                
        except Exception as e:
            logger.error(f"[VALIDACIÓN MASIVA] ERROR Excepción inesperada validando registro {i}: {str(e)}")
            error_info = {
                'registro': registro_data,
                'errors': [f"ERROR Error interno durante la validación: {str(e)}"],
                'tipos_error': ['error_interno'],
                'row_number': i
            }
            registros_invalidos.append(error_info)
    
    logger.info(
        f"[VALIDACIÓN MASIVA] Completada: {len(registros_validos)} válidos, "
        f"{len(registros_invalidos)} inválidos de {len(registros_data)} total"
    )
    
    return registros_validos, registros_invalidos

def format_validation_errors(errors: List[Dict]) -> str:
    """
    Formatea los errores de validación para mostrar al usuario.
    """
    if not errors:
        return "No hay errores de validación."
    
    formatted_errors = []
    for error in errors:
        row_num = error.get('row_number', 'N/A')
        registro = error.get('registro', {})
        nombre = registro.get('nombre', 'SIN NOMBRE')
        error_messages = error.get('errors', [])
        
        formatted_errors.append(f"Fila {row_num} ({nombre}):")
        for msg in error_messages:
            formatted_errors.append(f"  - {msg}")
        formatted_errors.append("")
    
    return "\n".join(formatted_errors)

def validate_celular(celular: str) -> Tuple[bool, str]:
    """
    Valida que el celular sea numérico y tenga exactamente 10 dígitos.
    """
    if not celular:
        return True, ""  # Campo opcional
    
    # Remover espacios y caracteres no numéricos
    celular_limpio = re.sub(r'[^\d]', '', str(celular))
    
    if not celular_limpio.isdigit():
        return False, f"El celular '{celular}' debe contener solo números"
    
    if len(celular_limpio) != 10:
        return False, f"El celular '{celular}' debe tener exactamente 10 dígitos (actualmente tiene {len(celular_limpio)})"
    
    return True, ""

def validate_correo(correo: str) -> Tuple[bool, str]:
    """
    Valida que el correo tenga un formato de email válido.
    """
    if not correo:
        return True, ""  # Campo opcional
    
    # Patrón básico para validar email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, correo):
        return False, f"El correo '{correo}' no tiene un formato de email válido"
    
    return True, ""

def validate_campo_texto(campo: str, nombre_campo: str) -> Tuple[bool, str]:
    """
    Valida que el campo de texto no contenga caracteres problemáticos.
    """
    if not campo:
        return True, ""  # Campo opcional
    
    # Verificar caracteres problemáticos
    caracteres_problematicos = ['<', '>', '&', '"', "'", '\\', '/', '|', ';', ':', '*', '?']
    for char in caracteres_problematicos:
        if char in campo:
            return False, f"El campo '{nombre_campo}' no puede contener el carácter '{char}'"
    
    return True, ""

def validate_campo_requerido(campo: str, nombre_campo: str) -> Tuple[bool, str]:
    """
    Valida que el campo requerido no esté vacío.
    """
    if not campo or str(campo).strip() == '':
        return False, f"El campo '{nombre_campo}' es requerido y no puede estar vacío"
    
    return True, "" 
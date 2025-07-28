import logging
import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Dict, Tuple
from pandas.errors import ParserError
import io
from sqlalchemy import text

from app.db.connection import get_async_session
from app.db.models import Registro
from app.schemas.registro import RegistroCreate
from app.services.validation import validate_bulk_registros
from app.services.deps import require_admin

logger = logging.getLogger(__name__)
router = APIRouter()

def clean_bom_from_headers(df_columns: List[str]) -> List[str]:
    """
    Limpia caracteres BOM de los headers del CSV.
    """
    cleaned_columns = []
    for col in df_columns:
        # Remover BOM y otros caracteres invisibles
        cleaned_col = col.strip().replace('\ufeff', '').replace('\u200b', '')
        cleaned_columns.append(cleaned_col)
        if col != cleaned_col:
            logger.info(f"BOM detectado y removido del header: '{col}' -> '{cleaned_col}'")
    return cleaned_columns

def map_spanish_columns_to_english(df_columns: List[str]) -> Dict[str, str]:
    """
    Mapea nombres de columnas en español a nombres en inglés.
    Retorna un diccionario con el mapeo de columnas.
    """
    column_mapping = {
        # Mapeo de español a inglés
        'Número de inspector': 'numero_inspector',
        'Número Inspector': 'numero_inspector',
        'Numero de inspector': 'numero_inspector',
        'Numero Inspector': 'numero_inspector',
        'Número': 'numero_inspector',
        'Numero': 'numero_inspector',
        
        'Nombre': 'nombre',
        'Name': 'nombre',
        
        'Status': 'status',
        'Estado': 'status',
        'Estado del registro': 'status',
        
        'Observaciones': 'observaciones',
        'Observación': 'observaciones',
        'Observacion': 'observaciones',
        
        'Región': 'region',
        'Region': 'region',
        
        'Flota': 'flota',
        
        'Encargado': 'encargado',
        'Supervisor': 'encargado',
        
        'Celular': 'celular',
        'Teléfono': 'celular',
        'Telefono': 'celular',
        'Phone': 'celular',
        
        'Correo': 'correo',
        'Email': 'correo',
        'E-mail': 'correo',
        
        'Dirección': 'direccion',
        'Direccion': 'direccion',
        'Address': 'direccion',
        
        'Uso': 'uso',
        'Use': 'uso',
        
        'Departamento': 'departamento',
        'Depto': 'departamento',
        
        'Ciudad': 'ciudad',
        'City': 'ciudad',
        
        'Tecnología': 'tecnologia',
        'Tecnologia': 'tecnologia',
        'Technology': 'tecnologia',
        
        'CMTS/OLT': 'cmts_olt',
        'CMTS OLT': 'cmts_olt',
        'CMTS': 'cmts_olt',
        
        'ID Servicio': 'id_servicio',
        'ID de Servicio': 'id_servicio',
        'Id Servicio': 'id_servicio',
        'Service ID': 'id_servicio',
        
        'MAC/SN': 'mac_sn',
        'MAC SN': 'mac_sn',
        'MAC': 'mac_sn',
        'Serial Number': 'mac_sn',
        
        'UUID': 'uuid',
        'uuid': 'uuid'
    }
    
    # Crear mapeo para las columnas que existen en el DataFrame
    actual_mapping = {}
    for spanish_col in df_columns:
        if spanish_col in column_mapping:
            actual_mapping[spanish_col] = column_mapping[spanish_col]
            logger.info(f"Mapeo de columna: '{spanish_col}' -> '{column_mapping[spanish_col]}'")
        else:
            # Si no hay mapeo, mantener el nombre original
            actual_mapping[spanish_col] = spanish_col
            logger.debug(f"Columna sin mapeo (manteniendo original): '{spanish_col}'")
    
    return actual_mapping

def validate_required_columns(df_columns: List[str], column_mapping: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Valida que el CSV contenga las columnas requeridas después del mapeo.
    Retorna (es_válido, lista_de_columnas_faltantes)
    """
    required_columns = ['numero_inspector', 'nombre', 'status']
    missing_columns = []
    
    # Obtener las columnas mapeadas
    mapped_columns = list(column_mapping.values())
    
    for col in required_columns:
        if col not in mapped_columns:
            missing_columns.append(col)
    
    if missing_columns:
        logger.error(f"ERROR Columnas requeridas faltantes después del mapeo: {missing_columns}")
        return False, missing_columns
    
    logger.info(f"OK Todas las columnas requeridas están presentes después del mapeo: {required_columns}")
    return True, []

@router.post("/upload_csv", summary="Carga masiva de registros desde archivo CSV")
async def upload_csv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(require_admin)
):
    """
    Endpoint para cargar registros desde un archivo CSV.
    Realiza todas las validaciones ANTES de modificar la base de datos.
    Si todo es válido, borra e inserta en una sola transacción.
    """
    logger.info(f"INICIO ===== CARGA MASIVA INICIADA =====")
    logger.info(f"Archivo recibido: {file.filename} ({file.content_type})")
    
    # Validar tipo de archivo
    if not file.filename.lower().endswith('.csv'):
        logger.error(f"ERROR Tipo de archivo no válido: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Tipo de archivo no válido",
                "message": "Solo se permiten archivos CSV."
            }
        )
    try:
        content = await file.read()
        logger.info(f"Archivo leído: {len(content)} bytes")
        # Leer el CSV detectando automáticamente el separador correcto (al menos 2 columnas)
        df = None
        separadores = [',', ';', '\t', '|']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        for encoding in encodings:
            for sep in separadores:
                try:
                    temp_df = pd.read_csv(io.BytesIO(content), encoding=encoding, sep=sep)
                    if len(temp_df.columns) >= 2:
                        df = temp_df
                        logger.info(f"DataFrame creado con encoding '{encoding}' y separador '{sep}': {len(df)} filas, {len(df.columns)} columnas")
                        break
                    else:
                        logger.debug(f"Intento con encoding '{encoding}' y separador '{sep}' resultó en {len(temp_df.columns)} columna(s), probando siguiente...")
                except Exception as e:
                    logger.debug(f"Error con encoding '{encoding}' y separador '{sep}': {str(e)}")
                    continue
            if df is not None:
                break
        if df is None or len(df.columns) < 2:
            logger.error(f"ERROR No se pudo leer el archivo CSV correctamente. Se intentaron encodings: {encodings} y separadores: {separadores}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error al leer archivo CSV",
                    "message": "No se pudo detectar el formato correcto del archivo CSV. Verifica el separador (coma, punto y coma, tabulador, etc.)."
                }
            )
        # Validación: No deben haber filas duplicadas en 'Número de inspector'
        if 'Número de inspector' in df.columns:
            duplicados = df['Número de inspector'][df['Número de inspector'].duplicated(keep=False)]
            if not duplicados.empty:
                filas_duplicadas = duplicados.unique().tolist()
                logger.error(f"ERROR: Se encontraron valores duplicados en 'Número de inspector': {filas_duplicadas}")
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Duplicados en Número de inspector",
                        "message": f"No se permite cargar el archivo porque hay valores duplicados en la columna 'Número de inspector': {filas_duplicadas}",
                        "duplicados": filas_duplicadas
                    }
                )
        # Filtrar solo las columnas requeridas
        columnas_requeridas = [
            'Número de inspector', 'Nombre', 'Observaciones', 'Status', 'Región', 'Flota', 'Encargado',
            'Celular', 'Correo', 'Dirección', 'Uso', 'Departamento', 'Ciudad', 'Tecnología', 'CMTS/OLT',
            'ID Servicio', 'MAC/SN', 'UUID'
        ]
        columnas_presentes = [col for col in columnas_requeridas if col in df.columns]
        df = df[columnas_presentes]
        # Validaciones por columna
        errores_validacion = []
        import re
        email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
        for idx, row in df.iterrows():
            fila = idx + 2  # Considerando encabezado
            num_inspector = str(row.get('Número de inspector', '')).strip()
            celular = str(row.get('Celular', '')).strip()
            correo = str(row.get('Correo', '')).strip()
            # Validar Número de inspector
            if not num_inspector.isdigit():
                errores_validacion.append({"fila": fila, "columna": "Número de inspector", "valor": num_inspector, "error": "Debe ser numérico"})
            # Validar Celular
            if celular and (not celular.isdigit() or len(celular) != 10):
                errores_validacion.append({"fila": fila, "columna": "Celular", "valor": celular, "error": "Debe ser numérico de 10 dígitos"})
            # Validar Correo
            if correo and not email_regex.match(correo):
                errores_validacion.append({"fila": fila, "columna": "Correo", "valor": correo, "error": "Debe ser un correo válido"})
        # Validación especial: 'Número de inspector' debe coincidir con el número después de 'ins' en 'Nombre'
        for idx, row in df.iterrows():
            fila = idx + 2
            num_inspector = str(row.get('Número de inspector', '')).strip()
            nombre = str(row.get('Nombre', '')).strip()
            if num_inspector.isdigit():
                if len(num_inspector) == 1:
                    patron1 = f"ins{num_inspector}"  # ins3
                    patron2 = f"ins0{num_inspector}" # ins03
                    if patron1 not in nombre and patron2 not in nombre:
                        errores_validacion.append({"fila": fila, "columna": "Nombre", "valor": nombre, "error": f"Debe contener 'ins{num_inspector}' o 'ins0{num_inspector}'"})
                else:
                    patron = f"ins{num_inspector}"
                    if patron not in nombre:
                        errores_validacion.append({"fila": fila, "columna": "Nombre", "valor": nombre, "error": f"Debe contener 'ins{num_inspector}'"})
        if errores_validacion:
            logger.error(f"Errores de validación por columna: {errores_validacion}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Errores de validación por columna",
                    "errores": errores_validacion
                }
            )
        # Si no hay errores, borrar e insertar
        from app.db.models import Registro
        async with session.begin():
            await session.execute(text("DELETE FROM registros"))
            nuevos_registros = []
            for _, row in df.iterrows():
                nuevo = Registro(
                    numero_inspector=int(row.get('Número de inspector', 0)),
                    nombre=str(row.get('Nombre', '')),
                    observaciones=str(row.get('Observaciones', '')),
                    status=str(row.get('Status', '')),
                    region=str(row.get('Región', '')),
                    flota=str(row.get('Flota', '')),
                    encargado=str(row.get('Encargado', '')),
                    celular=str(row.get('Celular', '')),
                    correo=str(row.get('Correo', '')),
                    direccion=str(row.get('Dirección', '')),
                    uso=str(row.get('Uso', '')),
                    departamento=str(row.get('Departamento', '')),
                    ciudad=str(row.get('Ciudad', '')),
                    tecnologia=str(row.get('Tecnología', '')),
                    cmts_olt=str(row.get('CMTS/OLT', '')),
                    id_servicio=str(row.get('ID Servicio', '')),
                    mac_sn=str(row.get('MAC/SN', '')),
                    uuid=str(row.get('UUID', '')) if 'UUID' in row else None
                )
                nuevos_registros.append(nuevo)
            session.add_all(nuevos_registros)
            await session.commit()
        return {"mensaje": "Carga masiva exitosa. Se reemplazaron todos los registros.", "total_registros": len(df)}

    except HTTPException:
        raise
    except ParserError as pe:
        logger.error(f"ERROR Error de parseo de CSV: {pe}", exc_info=True)
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "Error de parseo CSV",
                "message": "El archivo CSV no tiene un formato válido. Verifica que esté correctamente formateado.",
                "parser_error": str(pe)
            }
        )
    except IntegrityError as ie:
        logger.error(f"ERROR Error de integridad en la base de datos: {ie}", exc_info=True)
        raise HTTPException(
            status_code=409, 
            detail={
                "error": "Conflicto de datos",
                "message": "Los datos del archivo entran en conflicto con registros existentes en la base de datos."
            }
        )
    except SQLAlchemyError as se:
        logger.error(f"ERROR Error de base de datos: {se}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Error de base de datos",
                "message": "Error interno de base de datos al cargar los registros."
            }
        )
    except Exception as e:
        import traceback
        print('ERROR Error inesperado al procesar el archivo:', e)
        traceback.print_exc()
        logger.error(f"ERROR Error inesperado al procesar el archivo: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "error": "Error interno",
                "message": "Error interno del servidor al procesar el archivo.",
                "exception": str(e)
            }
        ) 
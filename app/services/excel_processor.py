import pandas as pd
from app.db.models import Registro
import logging

# Configuración básica del logger
logger = logging.getLogger(__name__)

async def procesar_excel(file):
    try:
        # Leer el archivo CSV con encoding UTF-8 para manejar acentos
        df = pd.read_csv(file.file, encoding='utf-8')
        logger.info("Archivo CSV leído correctamente.")

        # Llenar valores faltantes con cadenas vacías
        df = df.fillna("")

        # Mapeo de encabezados del CSV a nombres de campos del modelo
        mapeo_campos = {
            "Número de inspector": "numero_inspector",
            "Nombre": "nombre",
            "Status": "status",
            "Observaciones": "observaciones",
            "Flota": "flota",
            "Uso": "uso",
            "Encargado": "encargado",
            "Correo": "correo",
            "Celular": "celular",
            "Región": "region",
            "Departamento": "departamento",
            "Ciudad": "ciudad",
            "Dirección": "direccion",
            "ID Servicio": "id_servicio",
            "Tecnología": "tecnologia",
            "CMTS/OLT": "cmts_olt",
            "MAC/SN": "mac_sn"
        }

        # Renombrar columnas según el mapeo
        df = df.rename(columns=mapeo_campos)

        # Asegurar que las columnas de tipo texto sean string
        columnas_str = [
            "nombre", "observaciones", "status", "region",
            "flota", "encargado", "correo", "direccion", "uso", "departamento",
            "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn", "celular"
        ]
        for col in columnas_str:
            if col in df.columns:
                df[col] = df[col].astype(str)

        # Asegurar tipo numérico en columna 'numero_inspector'
        if "numero_inspector" in df.columns:
            df["numero_inspector"] = pd.to_numeric(df["numero_inspector"], errors="coerce").fillna(0).astype(int)

        registros = []
        for _, row in df.iterrows():
            registro = Registro(
                numero_inspector=row.get("numero_inspector", 0),
                nombre=row.get("nombre", ""),
                observaciones=row.get("observaciones", ""),
                status=row.get("status", ""),
                region=row.get("region", ""),
                flota=row.get("flota", ""),
                encargado=row.get("encargado", ""),
                celular=str(row.get("celular", "")),
                correo=row.get("correo", ""),
                direccion=row.get("direccion", ""),
                uso=row.get("uso", ""),
                departamento=row.get("departamento", ""),
                ciudad=row.get("ciudad", ""),
                tecnologia=row.get("tecnologia", ""),
                cmts_olt=row.get("cmts_olt", ""),
                id_servicio=row.get("id_servicio", ""),
                mac_sn=row.get("mac_sn", "")
            )
            registros.append(registro)
        logger.info(f"Procesados {len(registros)} registros desde el CSV.")
        return registros
    except Exception as e:
        logger.error(f"Error al procesar el archivo CSV: {e}")
        raise

"""
Utilidad para determinar el estado real de un dispositivo.
Replica la lógica del frontend (deviceStatus.ts) en Python.
"""

def get_device_real_status(device: dict) -> str:
    """
    Determina el estado real de un dispositivo aplicando la lógica de prioridad:
    1. Si la nota contiene "Libre" → Libre (prioridad absoluta)
    2. Si no, usa iddevicestatus
    
    Args:
        device: Diccionario con los datos del dispositivo
        
    Returns:
        str: 'libre', 'operativo', 'desconectado', o 'reducido'
    """
    # PRIORIDAD 1: Nota con "Libre"
    note = device.get('strnote', '')
    if note and 'libre' in note.lower():
        return 'libre'
    
    # PRIORIDAD 2: iddevicestatus
    status_id = device.get('iddevicestatus', 0)
    
    if status_id == 4:
        return 'libre'
    elif status_id in [3, 8]:
        return 'desconectado'
    elif status_id in [2, 9]:
        return 'reducido'
    elif status_id in [1, 5, 6, 7]:
        return 'operativo'
    
    # Fallback
    return 'desconectado'

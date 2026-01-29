#device_admin.py
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Depends, Request
from src.services.device_admin_service import DeviceAdminService
from src.services.balena_service import BalenaService
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest
from src.api.v1.schemas.device_action_schema import DeviceNoteRequest, DeviceMoveRequest, BulkActionRequest
from fastapi.responses import StreamingResponse
from src.core.security import require_roles
from src.core.celery_app import celery_app
from src.core.logger import logger
from typing import List


router = APIRouter()

def _resolve_identity(x_user_id: str, x_user_sub: str, x_user_email: str, x_role: str):
    """
    Helper para resolver la identidad del usuario y filtrar el rol relevante.
    """
    # 1. Resolver Usuario (Prioridad: Email > ID > Sub)
    final_user = x_user_email if x_user_email and x_user_email != "SYSTEM" else x_user_id
    if not final_user or final_user == "SYSTEM":
        if x_user_sub and x_user_sub != "SYSTEM": final_user = x_user_sub
    
    # 2. Resolver Rol (Filtrar solo Inspector_* y truncar)
    final_role = "SYSTEM"
    if x_role and x_role != "SYSTEM":
        roles = [r.strip() for r in x_role.split(",")]
        # Buscar el primer rol que empiece por 'Inspector_'
        inspector_role = next((r for r in roles if r.startswith("Inspector_")), None)
        
        if inspector_role:
            final_role = inspector_role[:50]
        else:
            # Si no hay rol Inspector, usar el primero de la lista (truncado)
            final_role = roles[0][:50]
            
    return final_user, final_role


@router.post("/{uuid}/provision")
async def provision_device_endpoint(
    uuid: str, 
    request: ProvisioningRequest,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.provision_device(uuid, request, user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/bulk/{action}", status_code=202)
async def bulk_power_action_endpoint(
    action: str,
    request: BulkActionRequest,
    request_obj: Request, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"),
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Ejecuta una acción de poder en múltiples dispositivos usando Celery.
    Válido para: restart, reboot, shutdown
    """
    # DEBUG: Log all headers
    logger.info("============== DEBUG HEADERS ==============")
    for key, value in request_obj.headers.items():
        logger.info(f"{key}: {value}")
    logger.info("===========================================")

    if action not in ["restart", "reboot", "shutdown"]:
        raise HTTPException(status_code=400, detail="Acción inválida. Use: restart, reboot o shutdown")
    
    if not request.uuids or len(request.uuids) == 0:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un UUID")

    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)
    
    logger.info(f"User resolved as: {final_user} (ID: {x_user_id}, Email: {x_user_email}, Sub: {x_user_sub})")
    logger.info(f"Role resolved as: {final_role} (Original: {x_role})")

    task = celery_app.send_task("tasks.restart_bulk_devices", args=[request.uuids, action, final_user, final_role])
    return {
        "success": True, 
        "message": f"{len(request.uuids)} dispositivos encolados para {action}.", 
        "task_id": task.id,
        "total_devices": len(request.uuids)
    }

@router.post("/{uuid}/reboot", status_code=202)
async def reboot_device_endpoint(
    uuid: str,
    request_obj: Request,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Reinicia el dispositivo (OS) usando Celery.
    """
    # DEBUG: Log all headers
    logger.info(f"============== DEBUG HEADERS ({uuid}) ==============")
    for key, value in request_obj.headers.items():
        logger.info(f"{key}: {value}")
    logger.info("===========================================")

    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)

    logger.info(f"User resolved as: {final_user} (ID: {x_user_id}, Email: {x_user_email}, Sub: {x_user_sub})")
    logger.info(f"Role resolved as: {final_role} (Original: {x_role})")

    task = celery_app.send_task("tasks.restart_single_device", args=[uuid, "reboot", final_user, final_role])
    return {"success": True, "message": "Reinicio de sistema encolado.", "task_id": task.id}

@router.post("/{uuid}/restart", status_code=202)
async def restart_container_endpoint(
    uuid: str,
    request_obj: Request,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Reinicia la aplicación (Contenedor) usando Celery.
    """
    # DEBUG: Log all headers
    logger.info(f"============== DEBUG HEADERS ({uuid}) ==============")
    for key, value in request_obj.headers.items():
        logger.info(f"{key}: {value}")
    logger.info("===========================================")

    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)

    logger.info(f"User resolved as: {final_user} (ID: {x_user_id}, Email: {x_user_email}, Sub: {x_user_sub})")
    logger.info(f"Role resolved as: {final_role} (Original: {x_role})")
    
    task = celery_app.send_task("tasks.restart_single_device", args=[uuid, "restart", final_user, final_role])
    return {"success": True, "message": "Reinicio de aplicación encolado.", "task_id": task.id}

@router.post("/{uuid}/shutdown", status_code=202)
async def shutdown_device_endpoint(
    uuid: str,
    request_obj: Request,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Apaga el dispositivo usando Celery.
    """
    # DEBUG: Log all headers
    logger.info(f"============== DEBUG HEADERS ({uuid}) ==============")
    for key, value in request_obj.headers.items():
        logger.info(f"{key}: {value}")
    logger.info("===========================================")

    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)

    logger.info(f"User resolved as: {final_user} (ID: {x_user_id}, Email: {x_user_email}, Sub: {x_user_sub})")
    logger.info(f"Role resolved as: {final_role} (Original: {x_role})")

    task = celery_app.send_task("tasks.restart_single_device", args=[uuid, "shutdown", final_user, final_role])
    return {"success": True, "message": "Apagado encolado.", "task_id": task.id}

@router.put("/{uuid}/note")
async def set_device_note_endpoint(
    uuid: str, 
    request: DeviceNoteRequest,
    request_obj: Request, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    # DEBUG: Log all headers
    logger.info(f"============== DEBUG HEADERS ({uuid}) ==============")
    for key, value in request_obj.headers.items():
        logger.info(f"{key}: {value}")
    logger.info("===========================================")

    # Fallback de identidad
    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)
        
    logger.info(f"User resolved as: {final_user} (ID: {x_user_id}, Email: {x_user_email}, Sub: {x_user_sub})")
    logger.info(f"Role resolved as: {final_role} (Original: {x_role})")

    result = await DeviceAdminService.set_note(uuid, request, user=final_user, role=final_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/{uuid}/move")
async def move_device_endpoint(
    uuid: str, 
    request: DeviceMoveRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)
        
    result = await DeviceAdminService.move_device_to_fleet(uuid, request.target_fleet, user=final_user, role=final_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- Endpoint antiguo de Provision (Recomendado: Eliminar si ya usas el de arriba con {uuid}) ---
@router.post("/provision")
async def provision_device(
    request: ProvisioningRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    if not request.uuid:
        raise HTTPException(status_code=400, detail="El UUID es obligatorio")

    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)

    result = await DeviceAdminService.provision_device(request.uuid, request, user=final_user, role=final_role)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
        
    return result

@router.get("/{uuid}/logs")
async def get_device_logs_stream(
    uuid: str,
    # Ahora coincide con el nombre en security.py
    user_data=Depends(require_roles(["Inspector_admin", "Inspector_operator"]))
):
    """
    Streaming en tiempo real de los logs del dispositivo.
    Bypass: Frontend -> Backend (Puerto 5000)
    """
    log_generator = BalenaService.stream_device_logs(uuid)
    
    headers = {
        "X-Accel-Buffering": "no",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    
    return StreamingResponse(log_generator, media_type="text/event-stream", headers=headers)

@router.delete("/{uuid}")
async def delete_device_endpoint(
    uuid: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_user_sub: str = Header("SYSTEM", alias="X-User-Sub"),
    x_user_email: str = Header("SYSTEM", alias="X-User-Email"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Elimina un dispositivo de la base de datos y de Balena Cloud.
    Mantiene el historial de métricas.
    """
    # Resolver entidad y rol filtrado
    final_user, final_role = _resolve_identity(x_user_id, x_user_sub, x_user_email, x_role)

    result = await DeviceAdminService.remove_device(uuid, user=final_user, role=final_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result
@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")

):
    """
    Obtiene el estado detallado de una tarea de Celery.
    
    Estados posibles:
    - PENDING: Tarea encolada, aún no ha iniciado
    - STARTED: En progreso (comando enviado, esperando confirmación)
    - SUCCESS: Completada exitosamente (reinicio confirmado)
    - FAILURE: Falló (error o timeout)
    - REVOKED: Cancelada
    
    Retorna:
        {
            "task_id": str,
            "status": str,  # PENDING, STARTED, SUCCESS, FAILURE, REVOKED
            "result": dict | None,  # Resultado final si SUCCESS
            "error": str | None,  # Mensaje de error si FAILURE
            "meta": dict | None  # Metadata de progreso si STARTED
        }
    """
    task_result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None,
        "error": None,
        "meta": None
    }
    
    # STARTED - Tarea en progreso
    if task_result.status == "STARTED":
        response["meta"] = task_result.info  # {status: "in_progress", message: "...", uuid: "...", action: "..."}
    
    # SUCCESS - Tarea completada exitosamente
    elif task_result.status == "SUCCESS":
        response["result"] = task_result.result
    
    # FAILURE - Tarea falló
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
    
    # PENDING - Aún no ha iniciado (estado por defecto)
    # No necesita información adicional
    
    return response


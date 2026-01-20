#device_admin.py
from fastapi import APIRouter, HTTPException, Header, BackgroundTasks, Depends
from src.services.device_admin_service import DeviceAdminService
from src.services.balena_service import BalenaService
from src.api.v1.schemas.provisioning_schema import ProvisioningRequest
from src.api.v1.schemas.device_action_schema import DeviceNoteRequest, DeviceMoveRequest, BulkActionRequest
from fastapi.responses import StreamingResponse
from src.core.security import require_roles
from src.core.celery_app import celery_app
from typing import List

router = APIRouter()

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
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"),
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Ejecuta una acción de poder en múltiples dispositivos usando Celery.
    Válido para: restart, reboot, shutdown
    """
    if action not in ["restart", "reboot", "shutdown"]:
        raise HTTPException(status_code=400, detail="Acción inválida. Use: restart, reboot o shutdown")
    
    if not request.uuids or len(request.uuids) == 0:
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos un UUID")
    
    task = celery_app.send_task("tasks.restart_bulk_devices", args=[request.uuids, action, x_user_id, x_role])
    return {
        "success": True, 
        "message": f"{len(request.uuids)} dispositivos encolados para {action}.", 
        "task_id": task.id,
        "total_devices": len(request.uuids)
    }

@router.post("/{uuid}/reboot", status_code=202)
async def reboot_device_endpoint(
    uuid: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Reinicia el dispositivo (OS) usando Celery.
    """
    task = celery_app.send_task("tasks.restart_single_device", args=[uuid, "reboot", x_user_id, x_role])
    return {"success": True, "message": "Reinicio de sistema encolado.", "task_id": task.id}

@router.post("/{uuid}/restart", status_code=202)
async def restart_container_endpoint(
    uuid: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Reinicia la aplicación (Contenedor) usando Celery.
    """
    task = celery_app.send_task("tasks.restart_single_device", args=[uuid, "restart", x_user_id, x_role])
    return {"success": True, "message": "Reinicio de aplicación encolado.", "task_id": task.id}

@router.post("/{uuid}/shutdown", status_code=202)
async def shutdown_device_endpoint(
    uuid: str,
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Apaga el dispositivo usando Celery.
    """
    task = celery_app.send_task("tasks.restart_single_device", args=[uuid, "shutdown", x_user_id, x_role])
    return {"success": True, "message": "Apagado encolado.", "task_id": task.id}

@router.put("/{uuid}/note")
async def set_device_note_endpoint(
    uuid: str, 
    request: DeviceNoteRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.set_note(uuid, request, user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.post("/{uuid}/move")
async def move_device_endpoint(
    uuid: str, 
    request: DeviceMoveRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    result = await DeviceAdminService.move_device_to_fleet(uuid, request.target_fleet, user=x_user_id, role=x_role)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

# --- Endpoint antiguo de Provision (Recomendado: Eliminar si ya usas el de arriba con {uuid}) ---
@router.post("/provision")
async def provision_device(
    request: ProvisioningRequest, 
    x_user_id: str = Header("SYSTEM", alias="X-User-Id"), 
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    if not request.uuid:
        raise HTTPException(status_code=400, detail="El UUID es obligatorio")

    result = await DeviceAdminService.provision_device(request.uuid, request, user=x_user_id, role=x_role)
    
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
    x_role: str = Header("SYSTEM", alias="X-Role")
):
    """
    Elimina un dispositivo de la base de datos y de Balena Cloud.
    Mantiene el historial de métricas.
    """
    result = await DeviceAdminService.remove_device(uuid, user=x_user_id, role=x_role)
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
    Obtiene el estado de una tarea de Celery (PENDING, STARTED, SUCCESS, FAILURE, REVOKED).
    """
    task_result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": None
    }
    
    # Solo incluir resultado si terminó
    if task_result.ready():
        if task_result.successful():
            response["result"] = task_result.result
        else:
            # Si falló, el result suele ser la excepción str(e)
            response["result"] = str(task_result.result)
            
    return response

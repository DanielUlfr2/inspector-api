import { getToken, logout } from "./authService";

interface ApiRequestOptions extends RequestInit {
  skipAuth?: boolean; // Para endpoints que no requieren autenticación
}

export async function apiRequest(url: string, options: ApiRequestOptions = {}) {
  const { skipAuth = false, ...fetchOptions } = options;
  
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string> || {}),
  };

  // Agregar token de autenticación si no se omite
  if (!skipAuth) {
    const token = getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  // Detectar expiración de sesión
  if (response.status === 401 || response.status === 403) {
    // Solo hacer logout si no estamos ya en la página de login
    if (!window.location.pathname.includes('/')) {
      logout();
      
      // Mostrar mensaje al usuario
      showSessionExpiredMessage();
      
      // Redirigir al login
      window.location.href = "/";
    }
    
    throw new Error("Sesión expirada. Redirigiendo al login.");
  }

  // Si hay otros errores HTTP, lanzar error con detalles
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
  }

  return response;
}

// Función para mostrar mensaje de sesión expirada
function showSessionExpiredMessage() {
  // Crear un elemento de notificación temporal
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background-color: #ef4444;
    color: white;
    padding: 12px 20px;
    border-radius: 6px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    font-size: 14px;
    max-width: 300px;
    animation: slideIn 0.3s ease-out;
  `;
  
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 8px;">
      <span style="font-size: 16px;">⚠️</span>
      <span>Sesión expirada. Redirigiendo al login...</span>
    </div>
  `;
  
  // Agregar estilos de animación
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(notification);
  
  // Remover la notificación después de 5 segundos
  setTimeout(() => {
    if (notification.parentNode) {
      notification.parentNode.removeChild(notification);
    }
  }, 5000);
}

// Helper para peticiones GET
export async function apiGet(url: string, options: ApiRequestOptions = {}) {
  const response = await apiRequest(url, { ...options, method: 'GET' });
  return response.json();
}

// Helper para peticiones POST
export async function apiPost(url: string, data: any, options: ApiRequestOptions = {}) {
  const response = await apiRequest(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
}

// Helper para peticiones PUT
export async function apiPut(url: string, data: any, options: ApiRequestOptions = {}) {
  console.log("apiPut - URL:", url);
  console.log("apiPut - Data:", data);
  const response = await apiRequest(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(data),
  });
  const result = await response.json();
  console.log("apiPut - Response:", result);
  return result;
}

// Helper para peticiones DELETE
export async function apiDelete(url: string, options: ApiRequestOptions = {}) {
  const response = await apiRequest(url, { ...options, method: 'DELETE' });
  return response;
} 
import { apiGet, apiPost, apiPut, apiDelete } from "./apiClient";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function getUsers() {
  return apiGet(`${API_URL}/usuarios/`);
}

export async function getUserById(id: number) {
  return apiGet(`${API_URL}/usuarios/${id}`);
}

export async function createUser(data: any) {
  return apiPost(`${API_URL}/usuarios/`, data);
}

export async function updateUser(id: number, data: any) {
  return apiPut(`${API_URL}/usuarios/${id}`, data);
}

export async function deleteUser(id: number) {
  return apiDelete(`${API_URL}/usuarios/${id}`);
}

export async function resetUserPassword(id: number, newPassword: string) {
  return apiPost(`${API_URL}/usuarios/${id}/restablecer-contrasena`, { new_password: newPassword });
}

export async function uploadUserPhoto(id: number, file: File) {
  const formData = new FormData();
  formData.append("file", file);
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_URL}/usuarios/${id}/foto`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || "Error al subir la foto de perfil");
  }
  return await res.json();
}

export async function toggleUserActive(id: number) {
  return apiPut(`${API_URL}/usuarios/${id}/toggle-activo`, {});
}

export async function getUserHistory(id: number) {
  return apiGet(`${API_URL}/usuarios/${id}/historial`);
} 
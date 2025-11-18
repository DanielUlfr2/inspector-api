import { apiGet, apiPost, apiPut, apiDelete } from "./apiClient";
import { DEMO_USUARIOS } from "./demoData";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const isDemoMode =
  import.meta.env.VITE_DEMO_MODE === 'true' ||
  import.meta.env.MODE === 'demo';

export async function getUsers() {
  if (isDemoMode) {
    return DEMO_USUARIOS;
  }
  return apiGet(`${API_URL}/usuarios/`);
}

export async function getUserById(id: number) {
  if (isDemoMode) {
    const user = DEMO_USUARIOS.find(u => u.id === id);
    if (!user) throw new Error('Usuario no encontrado');
    return user;
  }
  return apiGet(`${API_URL}/usuarios/${id}`);
}

export async function createUser(data: any) {
  if (isDemoMode) {
    const newId = Math.max(...DEMO_USUARIOS.map(u => u.id), 0) + 1;
    const newUser = {
      ...data,
      id: newId,
      fecha_creacion: new Date().toISOString(),
      activo: true,
      foto_perfil: null
    };
    DEMO_USUARIOS.push(newUser);
    return newUser;
  }
  return apiPost(`${API_URL}/usuarios/`, data);
}

export async function updateUser(id: number, data: any) {
  if (isDemoMode) {
    const index = DEMO_USUARIOS.findIndex(u => u.id === id);
    if (index === -1) throw new Error('Usuario no encontrado');
    DEMO_USUARIOS[index] = { ...DEMO_USUARIOS[index], ...data };
    return DEMO_USUARIOS[index];
  }
  return apiPut(`${API_URL}/usuarios/${id}`, data);
}

export async function deleteUser(id: number) {
  if (isDemoMode) {
    const index = DEMO_USUARIOS.findIndex(u => u.id === id);
    if (index !== -1) {
      DEMO_USUARIOS.splice(index, 1);
    }
    return;
  }
  return apiDelete(`${API_URL}/usuarios/${id}`);
}

export async function resetUserPassword(id: number, newPassword: string) {
  if (isDemoMode) {
    return { message: 'Contraseña restablecida (demo)' };
  }
  return apiPost(`${API_URL}/usuarios/${id}/restablecer-contrasena`, { new_password: newPassword });
}

export async function uploadUserPhoto(id: number, file: File) {
  if (isDemoMode) {
    const user = DEMO_USUARIOS.find(u => u.id === id);
    if (user) {
      user.foto_perfil = `/static/fotos/demo_${id}.jpg`;
    }
    return { message: 'Foto actualizada (demo)', foto: `/static/fotos/demo_${id}.jpg` };
  }

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
  if (isDemoMode) {
    const user = DEMO_USUARIOS.find(u => u.id === id);
    if (user) {
      user.activo = !user.activo;
      return user;
    }
    throw new Error('Usuario no encontrado');
  }
  return apiPut(`${API_URL}/usuarios/${id}/toggle-activo`, {});
}

export async function getUserHistory(id: number) {
  if (isDemoMode) {
    return [
      {
        id: 1,
        usuario_id: id,
        fecha: new Date().toISOString(),
        admin_que_realizo_cambio: 'Demo Admin',
        accion: 'creacion',
        campo: null,
        valor_anterior: null,
        valor_nuevo: null,
        descripcion: 'Usuario creado (demo)'
      }
    ];
  }
  return apiGet(`${API_URL}/usuarios/${id}/historial`);
} 
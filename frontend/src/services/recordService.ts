import { apiGet, apiPost, apiPut, apiDelete } from "./apiClient";
import { Registro, RegistroCreate, RegistroUpdate, HistorialItem } from "../types/Registro";

export async function getRegistros({ limit = 10, offset = 0, sortBy = 'id', sortDir = 'asc', columnFilters = {} }: {
  limit: number,
  offset: number,
  sortBy?: string,
  sortDir?: 'asc' | 'desc',
  columnFilters?: { [key: string]: string }
}): Promise<Registro[]> {
  try {
    const params = new URLSearchParams({
      limit: String(limit),
      offset: String(offset),
      sort_by: sortBy,
      sort_dir: sortDir,
    });
    Object.entries(columnFilters).forEach(([key, value]) => {
      if (value && value.trim()) {
        params.append(key, value.trim());
      }
    });
    return await apiGet(`${import.meta.env.VITE_API_URL}/registros?${params.toString()}`);
  } catch (error) {
    console.error("[ERROR getRegistros]:", error);
    throw error;
  }
}

export async function getTotalRegistros(columnFilters: { [key: string]: string } = {}): Promise<{ total: number }> {
  try {
    const params = new URLSearchParams();
    Object.entries(columnFilters).forEach(([key, value]) => {
      if (value && value.trim() !== '') {
        params.append(key, value);
      }
    });
    
    const url = `${import.meta.env.VITE_API_URL}/registros/total${params.toString() ? `?${params.toString()}` : ''}`;
    return await apiGet(url);
  } catch (error) {
    console.error("[ERROR getTotalRegistros]:", error);
    throw error;
  }
}

export async function getHistorialInspector(numero_inspector: number): Promise<HistorialItem[]> {
  try {
    const data = await apiGet(`${import.meta.env.VITE_API_URL}/registros/${numero_inspector}/historial`);
    
    // Convertir los datos del backend al formato HistorialItem
    return data.map((item: any) => ({
      fecha: item.fecha || new Date().toLocaleDateString('es-ES'),
      descripcion: item.descripcion || `Registro del inspector ${numero_inspector}`,
      autor: item.autor || item.usuario || "Sistema",
      campo: item.campo,
      valor_anterior: item.valor_anterior,
      valor_nuevo: item.valor_nuevo,
      usuario: item.usuario || "Sistema"
    }));
  } catch (error) {
    console.error("Error al consultar historial:", error);
    throw error;
  }
}

export async function createRegistro(registro: RegistroCreate): Promise<Registro> {
  try {
    return await apiPost(`${import.meta.env.VITE_API_URL}/registros`, registro);
  } catch (error) {
    console.error("Error al crear registro:", error);
    throw error;
  }
}

export async function updateRegistro(id: number, registro: RegistroUpdate): Promise<Registro> {
  try {
    return await apiPut(`${import.meta.env.VITE_API_URL}/registros/${id}`, registro);
  } catch (error) {
    console.error("Error al actualizar registro:", error);
    throw error;
  }
}

export async function deleteRegistro(id: number): Promise<void> {
  try {
    await apiDelete(`${import.meta.env.VITE_API_URL}/registros/${id}`);
  } catch (error) {
    console.error("Error al eliminar registro:", error);
    throw error;
  }
}

export async function uploadCsvFile(file: File): Promise<any> {
  try {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/upload_csv`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!res.ok) {
      const error = await res.json();
      throw new Error(error.detail || "Error al subir CSV");
    }

    return await res.json();
  } catch (error) {
    console.error("Error al subir archivo CSV:", error);
    throw error;
  }
}

export async function exportarRegistrosCSV(): Promise<void> {
  try {
    const token = localStorage.getItem('token');

    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/export_excel`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Error al exportar registros");
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `registros_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    
    // Limpiar URL del objeto
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al exportar registros:", error);
    throw error;
  }
}

export function exportarRegistrosDesdeFrontend(registros: Registro[]): void {
  try {
    // Definir las columnas del CSV
    const columns = [
      "numero_inspector", "uuid", "nombre", "observaciones", "status", "region", "flota",
      "encargado", "celular", "correo", "direccion", "uso", "departamento",
      "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn"
    ];

    // Crear el contenido del CSV
    const csvContent = [
      // Encabezados
      columns.join(','),
      // Datos
      ...registros.map(registro => 
        columns.map(col => {
          const value = registro[col as keyof Registro];
          // Escapar comas y comillas en los valores
          const escapedValue = String(value || '').replace(/"/g, '""');
          return `"${escapedValue}"`;
        }).join(',')
      )
    ].join('\n');

    // Crear el blob y descargar
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement("a");
    a.href = url;
    a.download = `registros_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    
    // Limpiar URL del objeto
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error al exportar registros desde frontend:", error);
    throw error;
  }
}

export async function getUniqueValues(col: string, search: string = ""): Promise<string[]> {
  try {
    const params = new URLSearchParams({ col });
    if (search) params.append("search", search);
    const res = await apiGet(`${import.meta.env.VITE_API_URL}/registros/unique_values?${params.toString()}`);
    return res.values || [];
  } catch (err) {
    console.error("[ERROR getUniqueValues]", err);
    return [];
  }
}

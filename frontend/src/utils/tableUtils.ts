// src/utils/tableUtils.ts

export function calcularTotalPaginas(totalRegistros: number, registrosPorPagina: number): number {
  return Math.ceil(totalRegistros / registrosPorPagina);
}

export function obtenerOffset(paginaActual: number, registrosPorPagina: number): number {
  return (paginaActual - 1) * registrosPorPagina;
}

export function formatoCampo(campo: string): string {
  return campo.replace(/_/g, " ");
} 
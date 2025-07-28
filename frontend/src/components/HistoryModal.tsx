import React, { useEffect, useState, useMemo } from "react";
import "./HistoryModal.css";
import { HistorialItem } from "../types/Registro";

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  inspectorId: number | null;
  historial: HistorialItem[];
}

const HistoryModal: React.FC<HistoryModalProps> = ({ isOpen, onClose, inspectorId, historial }) => {
  const [pagina, setPagina] = useState(1);
  const [registrosPorPagina] = useState(5);
  const [filtroTipo, setFiltroTipo] = useState<string>("");
  const [filtroFecha, setFiltroFecha] = useState<string>("");
  const [filtroCampo, setFiltroCampo] = useState<string>("");

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [onClose]);

  // Resetear página cuando cambien los filtros
  useEffect(() => {
    setPagina(1);
  }, [filtroTipo, filtroFecha, filtroCampo]);

  // Filtrar historial
  const historialFiltrado = useMemo(() => {
    return historial.filter(item => {
      const cumpleTipo = !filtroTipo || item.descripcion.toLowerCase().includes(filtroTipo.toLowerCase());
      const cumpleFecha = !filtroFecha || item.fecha.includes(filtroFecha);
      const cumpleCampo = !filtroCampo || (item.campo && item.campo.toLowerCase().includes(filtroCampo.toLowerCase()));
      
      return cumpleTipo && cumpleFecha && cumpleCampo;
    });
  }, [historial, filtroTipo, filtroFecha, filtroCampo]);

  // Calcular paginación
  const totalPaginas = Math.ceil(historialFiltrado.length / registrosPorPagina);
  const inicio = (pagina - 1) * registrosPorPagina;
  const historialPaginado = historialFiltrado.slice(inicio, inicio + registrosPorPagina);

  // Obtener campos únicos para el filtro
  const camposUnicos = useMemo(() => {
    const campos = historial
      .map(item => item.campo)
      .filter(campo => campo)
      .filter((campo, index, array) => array.indexOf(campo) === index);
    return campos;
  }, [historial]);

  // Obtener tipos únicos de cambio para autocompletado, filtrados por campo si hay filtroCampo
  const tiposUnicos = useMemo(() => {
    let historialFiltradoPorCampo = historial;
    if (filtroCampo) {
      historialFiltradoPorCampo = historial.filter(item => item.campo && item.campo.toLowerCase() === filtroCampo.toLowerCase());
    }
    const tipos = historialFiltradoPorCampo
      .map(item => item.descripcion)
      .filter(tipo => tipo)
      .map(tipo => tipo.trim())
      .filter((tipo, index, array) => array.indexOf(tipo) === index);
    return tipos;
  }, [historial, filtroCampo]);

  const limpiarFiltros = () => {
    setFiltroTipo("");
    setFiltroFecha("");
    setFiltroCampo("");
    setPagina(1);
  };

  // Función para exportar historial filtrado a JSON
  const exportarHistorialJSON = () => {
    const dataStr = JSON.stringify(historialFiltrado, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `historial_inspector_${inspectorId}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  if (!isOpen || inspectorId === null) return null;

  return (
    <div className="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal-content">
        <div className="modal-header">
          <h2 id="modal-title">Historial - Inspector #{inspectorId}</h2>
          <button 
            className="close-btn" 
            onClick={onClose} 
            aria-label="Cerrar modal"
            type="button"
          >
            ✖
          </button>
        </div>
        
        <div className="modal-body">
          {/* Filtros */}
          <div className="filtros-container">
            <div className="filtro-grupo">
              <label htmlFor="filtro-tipo">Tipo de cambio:</label>
              <input
                id="filtro-tipo"
                type="text"
                placeholder="Buscar en descripción..."
                value={filtroTipo}
                onChange={(e) => setFiltroTipo(e.target.value)}
                list="tipos-cambio"
              />
              <datalist id="tipos-cambio">
                {tiposUnicos.map(tipo => (
                  <option key={tipo} value={tipo} />
                ))}
              </datalist>
            </div>
            
            <div className="filtro-grupo">
              <label htmlFor="filtro-fecha">Fecha:</label>
              <input
                id="filtro-fecha"
                type="text"
                placeholder="YYYY-MM-DD o parte de fecha..."
                value={filtroFecha}
                onChange={(e) => setFiltroFecha(e.target.value)}
              />
            </div>
            
            <div className="filtro-grupo">
              <label htmlFor="filtro-campo">Campo:</label>
              <select
                id="filtro-campo"
                value={filtroCampo}
                onChange={(e) => setFiltroCampo(e.target.value)}
              >
                <option value="">Todos los campos</option>
                {camposUnicos.map(campo => (
                  <option key={campo} value={campo}>{campo}</option>
                ))}
              </select>
            </div>
            
            <button 
              className="btn-limpiar-filtros" 
              onClick={limpiarFiltros}
              type="button"
            >
              Limpiar filtros
            </button>
            <button
              className="btn-exportar-json"
              onClick={exportarHistorialJSON}
              type="button"
              style={{ marginLeft: 8 }}
            >
              Exportar JSON
            </button>
          </div>

          {/* Información de resultados */}
          <div className="resultados-info">
            <span>
              Mostrando {historialPaginado.length} de {historialFiltrado.length} registros
              {historialFiltrado.length !== historial.length && ` (filtrados de ${historial.length} total)`}
            </span>
          </div>

          {/* Lista de historial */}
          {historialPaginado.length === 0 ? (
            <p className="no-data">
              {historialFiltrado.length === 0 && historial.length > 0
                ? "No hay registros que coincidan con los filtros aplicados."
                : historial.length === 0
                  ? "No hay historial disponible para este inspector."
                  : "No hay historial reciente (últimos 15 días) para este inspector."
              }
            </p>
          ) : (
            <div className="historial-container">
              <ul className="historial-list">
                {historialPaginado.map((item, index) => (
                  <li key={index} className="historial-item">
                    <div className="historial-header">
                      <strong className="historial-fecha">{item.fecha}</strong>
                      <span className="historial-autor">por {item.autor}</span>
                    </div>
                    <div className="historial-descripcion">{item.descripcion}</div>
                    {item.campo && item.valor_anterior && item.valor_nuevo && (
                      <div className="historial-cambios">
                        <span className="campo-label">Campo: {item.campo}</span>
                        <div className="valores-cambio">
                          <span className="valor-anterior">Antes: {item.valor_anterior}</span>
                          <span className="valor-nuevo">Después: {item.valor_nuevo}</span>
                        </div>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Paginación */}
          {totalPaginas > 1 && (
            <div className="paginacion">
              <button 
                onClick={() => setPagina(p => Math.max(p - 1, 1))} 
                disabled={pagina === 1}
                className="btn-paginacion"
                type="button"
              >
                ◀ Anterior
              </button>
              <span className="pagina-info">
                Página {pagina} de {totalPaginas}
              </span>
              <button 
                onClick={() => setPagina(p => Math.min(p + 1, totalPaginas))} 
                disabled={pagina === totalPaginas}
                className="btn-paginacion"
                type="button"
              >
                Siguiente ▶
              </button>
            </div>
          )}
        </div>
        
        <div className="modal-footer">
          <button 
            className="btn-secondary" 
            onClick={onClose}
            type="button"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default HistoryModal;

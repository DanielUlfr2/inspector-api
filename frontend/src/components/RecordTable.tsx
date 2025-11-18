import React, { useEffect, useState, useRef } from "react";
import { useUser } from "../context/UserContext";
import { getRegistros, getTotalRegistros, getHistorialInspector, deleteRegistro, exportarRegistrosDesdeFrontend, getUniqueValues, exportarRegistrosCSV } from "../services/recordService";
import { calcularTotalPaginas, obtenerOffset, formatoCampo } from "../utils/tableUtils";
import { ROLES } from "../constants/roles";
import { Registro, HistorialItem } from "../types/Registro";
import { useNotification } from "../hooks/useNotification";
import Notification from "./Notification";
import EditModal from "./EditModal";
import CreateModal from "./CreateModal";
import BulkUploadModal from "./BulkUploadModal";
import ConfirmModal from "./ConfirmModal";
import "./RecordTable.css";
import HistoryModal from "./HistoryModal";
import { FiPlusCircle, FiUpload, FiEye, FiSearch, FiDownload, FiEdit, FiTrash2, FiClock } from "react-icons/fi";
import { apiGet } from "../services/apiClient";
// import Header from "./Header"; // Eliminar import innecesario

const columns = [
  "numero_inspector", "uuid", "nombre", "observaciones", "status", "region", "flota",
  "encargado", "celular", "correo", "direccion", "uso", "departamento",
  "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn"
];

function RecordTable() {
  const { rol } = useUser();
  const userRol = rol?.toLowerCase?.() || "";
  const [registros, setRegistros] = useState<Registro[]>([]);
  const [pagina, setPagina] = useState(1);
  const [totalRegistros, setTotalRegistros] = useState(0);
  const [registrosPorPagina] = useState(20);
  const [busqueda, setBusqueda] = useState("");
  const [busquedaTemp, setBusquedaTemp] = useState(""); // Estado temporal para el input
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedInspectorId, setSelectedInspectorId] = useState<number | null>(null);
  const [historial, setHistorial] = useState<HistorialItem[]>([]);
  const [cargando, setCargando] = useState(true);
  const [errorCarga, setErrorCarga] = useState(false);
  const [error, setError] = useState("");
  
  // Estados para el modal de edición
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [registroParaEditar, setRegistroParaEditar] = useState<Registro | null>(null);
  
  // Estados para el modal de creación
  const [createModalOpen, setCreateModalOpen] = useState(false);
  
  // Estados para el modal de carga masiva
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  
  // Estados para selección múltiple
  const [seleccionados, setSeleccionados] = useState<number[]>([]);
  
  // Estados para confirmación modal
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  const [registroAEliminar, setRegistroAEliminar] = useState<number | null>(null);
  const [mensajeConfirmacion, setMensajeConfirmacion] = useState("");
  const [tituloConfirmacion, setTituloConfirmacion] = useState("");
  const [tipoConfirmacion, setTipoConfirmacion] = useState<"danger" | "warning" | "info">("info");
  
  // Estados para filtros y ordenación por columna
  const [columnFilters, setColumnFilters] = useState<{ [key: string]: string }>({});
  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);
  // Estado para mostrar el filtro activo por columna
  const [activeFilterCol, setActiveFilterCol] = useState<string | null>(null);
  // Estado para la posición del popover de filtro
  const [filterPopover, setFilterPopover] = useState<{ col: string, anchor: HTMLElement | null } | null>(null);
  const [filterInput, setFilterInput] = useState('');
  const [uniqueValues, setUniqueValues] = useState<string[]>([]);
  const [loadingUnique, setLoadingUnique] = useState(false);
  // Estado para el tipo de filtro por columna
  const [filterMode, setFilterMode] = useState<{ [col: string]: 'partial' | 'exact' }>({});
  // Estado para saber qué columna tiene el filtro abierto
  const [openFilterCol, setOpenFilterCol] = useState<string | null>(null);
  // Estado para el modo de búsqueda global
  const [globalSearchMode, setGlobalSearchMode] = useState<'partial' | 'exact'>('partial');
  const globalDebounceTimeout = useRef<NodeJS.Timeout | null>(null);

  // Estado para debounce
  const debounceTimeout = useRef<NodeJS.Timeout | null>(null);

  // 1. Estado para fila con menú abierto
  const [menuRowId, setMenuRowId] = useState<number | null>(null);
  const [menuAnchor, setMenuAnchor] = useState<HTMLElement | null>(null);

  // 2. Función para abrir menú al hacer doble clic
  const handleRowDoubleClick = (rowId: number, event: React.MouseEvent<HTMLTableRowElement>) => {
    setMenuRowId(rowId);
    setMenuAnchor(event.currentTarget as HTMLElement);
  };

  // 3. Función para cerrar menú
  const handleCloseMenu = () => {
    setMenuRowId(null);
    setMenuAnchor(null);
  };

  // 4. Cerrar menú con ESC
  useEffect(() => {
    if (!menuRowId) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') handleCloseMenu();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [menuRowId]);

  // Asegúrate de que en el useEffect y en handleShowFilterPopover se use el nombre real de la columna
  // Si columns contiene alias o nombres formateados, crea un mapping de alias a nombre real
  // Por ejemplo:
  const columnMap: { [key: string]: string } = {
    'numero inspector': 'numero_inspector',
    'nombre': 'nombre',
    'observaciones': 'observaciones',
    'status': 'status',
    'region': 'region',
    'flota': 'flota',
    'encargado': 'encargado',
    'celular': 'celular',
    'correo': 'correo',
    'direccion': 'direccion',
    'uso': 'uso',
    'departamento': 'departamento',
    'ciudad': 'ciudad',
    'tecnologia': 'tecnologia',
    'cmts olt': 'cmts_olt',
    'id servicio': 'id_servicio',
    'mac sn': 'mac_sn',
  };

  // Luego, en el useEffect y handleShowFilterPopover:
  useEffect(() => {
    if (filterPopover) {
      setLoadingUnique(true);
      const realCol = columnMap[filterPopover.col] || filterPopover.col;
      getUniqueValues(realCol, filterInput).then(vals => {
        setUniqueValues(vals);
        setLoadingUnique(false);
      });
    }
  }, [filterPopover, filterInput]);
  
  const { notification, showSuccess, showError, hideNotification } = useNotification();

  // useEffect inicial para cargar datos al montar el componente
  useEffect(() => {
    fetchRegistros();
    fetchTotalRegistros();
  }, []); // Array vacío para ejecutar solo al montar

  // useEffect para recargar registros al cambiar sortConfig o página
  useEffect(() => {
    fetchRegistros();
    fetchTotalRegistros(); // Agregar llamada para actualizar el total
    // Limpiar selección cuando cambie la página o el orden
    setSeleccionados([]);
  }, [pagina, sortConfig]);

  // Guarda sortConfig en localStorage cada vez que cambie
  useEffect(() => {
    if (sortConfig) {
      localStorage.setItem('sortConfig', JSON.stringify(sortConfig));
    }
  }, [sortConfig]);

  // Función para alternar selección de un registro
  const toggleSeleccion = (id: number) => {
    setSeleccionados(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  // Función para alternar selección de todos los registros
  const toggleSeleccionTodos = () => {
    if (seleccionados.length === registros.length) {
      setSeleccionados([]);
    } else {
      setSeleccionados(registros.map(r => r.id));
    }
  };

  // Función para eliminar registros seleccionados
  const handleEliminarSeleccion = async () => {
    setMensajeConfirmacion(`¿Estás seguro de eliminar los ${seleccionados.length} registros seleccionados? Esta acción no se puede deshacer.`);
    setTituloConfirmacion("Confirmar eliminación múltiple");
    setTipoConfirmacion("danger");
    setConfirmModalVisible(true);
  };

  const confirmarEliminacionMultiple = async () => {
    for (const id of seleccionados) {
      try {
        await deleteRegistro(id);
      } catch (e) {
        console.error(`Error al eliminar ID ${id}:`, e);
      }
    }

    setSeleccionados([]);
    fetchRegistros(); // refrescar datos
    fetchTotalRegistros(); // actualizar total
    showSuccess("Registros eliminados con éxito.");
    setConfirmModalVisible(false);
  };

  const confirmarEliminacion = async () => {
    if (registroAEliminar !== null) {
      try {
        await deleteRegistro(registroAEliminar);
        showSuccess("Registro eliminado con éxito.");
        fetchRegistros(); // refrescar tabla
        fetchTotalRegistros(); // actualizar total
      } catch (error) {
        console.error("Error al eliminar:", error);
        showError("Error al eliminar el registro. Intenta nuevamente.");
      }
    }
    setConfirmModalVisible(false);
    setRegistroAEliminar(null);
  };

  const cancelarEliminacion = () => {
    setConfirmModalVisible(false);
    setRegistroAEliminar(null);
  };

  const handleConfirmacion = async () => {
    if (registroAEliminar !== null) {
      await confirmarEliminacion();
    } else {
      await confirmarEliminacionMultiple();
    }
  };

  // Función para exportar registros seleccionados
  const exportarSeleccionComoCSV = () => {
    const registrosSeleccionados = registros.filter(r => seleccionados.includes(r.id));
    try {
      exportarRegistrosDesdeFrontend(registrosSeleccionados);
      showSuccess("Registros exportados con éxito.");
    } catch (error) {
      console.error("Error al exportar registros:", error);
      showError("Error al exportar los registros. Intenta nuevamente.");
    }
  };

  // Modifica fetchRegistros para aceptar un parámetro exact
  const buildCombinedFilters = (exact = false) => {
    const filters = { ...columnFilters };
    Object.keys(filters).forEach(col => {
      if (filterMode[col] === 'exact' && filters[col]) {
        filters[col] = `__EXACT__${filters[col]}`;
      }
    });
    if (busqueda) {
      columns.forEach(col => {
        if (!filters[col]) { // Solo si no hay filtro individual
          if (exact && globalSearchMode === 'exact') {
            filters[col] = `__EXACT__${busqueda}`;
          } else {
            filters[col] = busqueda;
          }
        }
      });
    }
    return filters;
  };

  const fetchRegistros = (exact = false) => {
    setCargando(true);
    setErrorCarga(false);
    const offset = obtenerOffset(pagina, registrosPorPagina);
    const filters = buildCombinedFilters(exact);
    getRegistros({
      limit: registrosPorPagina,
      offset,
      sortBy: sortConfig?.key || 'id',
      sortDir: sortConfig?.direction || 'asc',
      columnFilters: filters,
    })
      .then(data => {
        if (Array.isArray(data)) {
          setRegistros(data);
        } else if (data && Array.isArray((data as any).registros)) {
          setRegistros((data as any).registros);
        } else {
          setRegistros([]);
          setError("La respuesta del servidor no es válida.");
        }
      })
      .catch(err => {
        setRegistros([]);
        setError("Error al obtener registros: " + err);
        setErrorCarga(true);
      })
      .finally(() => setCargando(false));
  };

  const fetchTotalRegistros = async (exact = false) => {
    const filters = buildCombinedFilters(exact);
    try {
      const res = await getTotalRegistros(filters);
      if (res && typeof (res as any).total === 'number') setTotalRegistros((res as any).total);
    } catch {
      setTotalRegistros(0);
    }
  };

  const handleOpenModal = async (numero_inspector: number) => {
    try {
      const historialData = await getHistorialInspector(numero_inspector);
      setHistorial(historialData);
      setSelectedInspectorId(numero_inspector);
      setIsModalOpen(true);
    } catch (error) {
      console.error("Error al abrir modal con historial:", error);
      showError("Error al cargar el historial del inspector. Intenta nuevamente.");
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedInspectorId(null);
    setHistorial([]);
  };

  const handleDelete = async (registroId: number) => {
    setRegistroAEliminar(registroId);
    setMensajeConfirmacion("¿Estás seguro de que deseas eliminar este registro? Esta acción no se puede deshacer.");
    setTituloConfirmacion("Confirmar eliminación");
    setTipoConfirmacion("danger");
    setConfirmModalVisible(true);
  };

  const handleEditClick = (registro: Registro) => {
    setRegistroParaEditar(registro);
    setEditModalOpen(true);
  };

  const handleEditSuccess = () => {
    fetchRegistros(); // refrescar tabla
    fetchTotalRegistros(); // actualizar total
  };

  const handleCloseEditModal = () => {
    setEditModalOpen(false);
    setRegistroParaEditar(null);
  };

  const handleCreateSuccess = () => {
    fetchRegistros(); // refrescar tabla
    fetchTotalRegistros(); // actualizar total
  };

  const handleCloseCreateModal = () => {
    setCreateModalOpen(false);
  };

  const handleUploadSuccess = () => {
    fetchRegistros(); // refrescar tabla
    fetchTotalRegistros(); // actualizar total
  };

  const handleCloseUploadModal = () => {
    setUploadModalOpen(false);
  };

  const handleBuscar = () => {
    setPagina(1); // Reinicia a página 1 al buscar
    fetchRegistros();
  };

  const handleBusquedaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBusquedaTemp(e.target.value);
    setGlobalSearchMode('partial');
  };

  const handleBusquedaKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setBusqueda(busquedaTemp);
      setGlobalSearchMode('exact');
    } else if (e.key === 'Escape') {
      setBusqueda("");
      setBusquedaTemp("");
      setGlobalSearchMode('partial');
      setPagina(1);
      fetchRegistros();
      fetchTotalRegistros();
    }
  };

  const handleBusquedaBlur = () => {
    setBusqueda(busquedaTemp);
    setGlobalSearchMode('exact');
  };

  const handleLimpiarBusqueda = () => {
    setBusqueda("");
    setBusquedaTemp("");
    setPagina(1);
  };

  const totalPaginas = calcularTotalPaginas(totalRegistros, registrosPorPagina);

  // Filtrado y ordenación en frontend
  // Eliminar filtrado y ordenamiento local
  // const filteredRegistros = ...
  // const sortedRegistros = ...

  // Usar directamente registros para renderizar la tabla

  const handleColumnFilterChange = (col: string, value: string) => {
    setColumnFilters(prev => ({ ...prev, [col]: value }));
    setFilterMode(prev => ({ ...prev, [col]: 'partial' }));
  };

  const handleColumnFilterKeyDown = (col: string, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setFilterMode(prev => ({ ...prev, [col]: 'exact' }));
    } else if (e.key === 'Escape') {
      setColumnFilters(prev => ({ ...prev, [col]: '' }));
      setFilterMode(prev => ({ ...prev, [col]: 'partial' }));
      fetchRegistros();
      fetchTotalRegistros();
      setOpenFilterCol(null);
    }
  };

  const handleColumnFilterBlur = (col: string) => {
    setFilterMode(prev => ({ ...prev, [col]: 'exact' }));
  };

  // useEffect para búsqueda reactiva parcial de filtros por columna
  useEffect(() => {
    // Si algún filtro de columna está en modo 'exact', no hacer debounce aquí
    const anyExact = Object.values(filterMode).some(mode => mode === 'exact');
    if (anyExact) return;
    if (debounceTimeout.current) clearTimeout(debounceTimeout.current);
    debounceTimeout.current = setTimeout(() => {
      fetchRegistros();
      fetchTotalRegistros();
    }, 400);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columnFilters, filterMode]);

  // useEffect para búsqueda exacta inmediata de filtros por columna
  useEffect(() => {
    // Si no hay ningún filtro en modo exacto, no hacer nada
    const anyExact = Object.values(filterMode).some(mode => mode === 'exact');
    if (!anyExact) return;
    fetchRegistros(true);
    fetchTotalRegistros(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterMode]);

  // useEffect para actualizar el total de registros al cambiar filtros o modo de filtro
  useEffect(() => {
    const fetchTotal = async () => {
      // Construye los filtros igual que en fetchRegistros
      const filters = buildCombinedFilters(true); // Use true for exact search
      try {
        const res = await getTotalRegistros(filters);
        if (res && typeof res.total === 'number') setTotalRegistros(res.total);
      } catch {
        setTotalRegistros(0);
      }
    };
    fetchTotal();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [columnFilters, filterMode, busqueda, globalSearchMode]);

  // useEffect para búsqueda reactiva parcial global (solo cuando busquedaTemp cambia y no es exacta)
  useEffect(() => {
    if (globalSearchMode === 'exact') return;
    if (globalDebounceTimeout.current) clearTimeout(globalDebounceTimeout.current);
    globalDebounceTimeout.current = setTimeout(() => {
      setBusqueda(busquedaTemp); // Actualiza el valor real solo después del debounce
    }, 1000); // 1 segundo
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busquedaTemp, globalSearchMode]);

  // useEffect para disparar fetch cuando busqueda cambia (parcial o exacta)
  useEffect(() => {
    fetchRegistros(globalSearchMode === 'exact');
    fetchTotalRegistros(globalSearchMode === 'exact');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busqueda, globalSearchMode]);

  // handleSort: cambia el orden y reinicia la página
  const handleSort = (col: string) => {
    setSortConfig(prev => {
      if (prev && prev.key === col) {
        return { key: col, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { key: col, direction: 'asc' };
    });
    setPagina(1);
  };

  const handleShowFilter = (col: string) => {
    setActiveFilterCol(col);
  };

  const handleShowFilterPopover = (col: string, event: React.MouseEvent<HTMLButtonElement>) => {
    setFilterPopover({ col: columnMap[col] || col, anchor: event.currentTarget });
    setFilterInput('');
    setUniqueValues([]);
  };

  const handleCloseFilterPopover = () => {
    setFilterPopover(null);
    setFilterInput('');
    setUniqueValues([]);
  };

  const handleFilterInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleColumnFilterChange(filterPopover!.col, filterInput);
      handleCloseFilterPopover();
    } else if (e.key === 'Escape') {
      handleCloseFilterPopover();
    }
  };

  const handleSelectUniqueValue = (val: string) => {
    handleColumnFilterChange(filterPopover!.col, val);
    handleCloseFilterPopover();
  };

  const handleClearFilter = () => {
    handleColumnFilterChange(filterPopover!.col, '');
    setFilterInput('');
    setUniqueValues([]);
    handleCloseFilterPopover();
  };

  // Función para exportar historial global
  const exportarHistorialGlobal = async () => {
    try {
      const data = await apiGet(`${import.meta.env.VITE_API_URL}/historial-cambios/exportar`);
      const dataStr = JSON.stringify(data, null, 2);
      const blob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `historial_cambios_global.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert("Error al exportar historial global");
    }
  };

  // const [showHeader, setShowHeader] = useState(true); // Eliminar estado innecesario

  return (
    <div className="record-table-container">
      {/* Header eliminado para evitar duplicados */}
      {error && <div className="error-message">{error}</div>}
      
      <div className="barra-insta" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 32 }}>
        <div className="busqueda-logo-row" style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
          <img src={`${import.meta.env.BASE_URL}logo-inspector.png`} alt="Inspector" style={{ height: 112, marginLeft: '2cm', marginRight: 24, borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }} />
          <input
            type="text"
            placeholder="Buscar en registros..."
            value={busquedaTemp}
            onChange={handleBusquedaChange}
            onKeyDown={handleBusquedaKeyDown}
            onBlur={handleBusquedaBlur}
            disabled={cargando}
            style={{ flex: 1, height: 56, fontSize: 18, borderRadius: 28, border: 'none', boxShadow: '0 2px 12px rgba(60,60,60,0.08)', padding: '0 32px', marginRight: 24, background: '#fff' }}
          />
        </div>
        <div className="acciones-app" style={{ display: 'flex', alignItems: 'center', gap: 24, marginLeft: 32 }}>
          {userRol === ROLES.ADMIN && (
            <>
              <button className="icon-btn-app" onClick={() => setCreateModalOpen(true)} disabled={cargando} title="Crear nuevo registro">
                <FiPlusCircle size={26} />
              </button>
              <button className="icon-btn-app" onClick={() => setUploadModalOpen(true)} disabled={cargando} title="Cargar CSV">
                <FiUpload size={26} />
              </button>
            </>
          )}
          <button className="icon-btn-app" onClick={exportarRegistrosCSV} disabled={cargando} title="Exportar todos">
            <FiDownload size={26} />
          </button>
          {userRol === ROLES.ADMIN && (
            <button className="icon-btn-app" onClick={exportarHistorialGlobal} disabled={cargando} title="Exportar historial de cambios">
              <FiEye size={26} />
            </button>
          )}
          <button className="icon-btn-app icon-btn-total" disabled title="Total de registros">
            <span className="total-number">{totalRegistros}</span>
          </button>
        </div>
      </div>
      
      <div className="tabla-wrapper">
        <table className="tabla-registros">
        <thead>
          <tr>
            {userRol === ROLES.ADMIN && (
                <th rowSpan={2}>
                <input
                  type="checkbox"
                  checked={seleccionados.length === registros.length && registros.length > 0}
                  onChange={toggleSeleccionTodos}
                />
              </th>
            )}
            {columns.map(col => (
              <th key={col} style={{ verticalAlign: 'bottom', position: 'relative', minWidth: 120 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 4, position: 'relative', width: '100%' }}>
                  {openFilterCol === col ? (
                    <>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ marginRight: 4 }}>
                        <circle cx="11" cy="11" r="7" stroke="#9ca3af" strokeWidth="2" />
                        <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" />
                      </svg>
                      <input
                        type="text"
                        className="col-filter-input"
                        placeholder={`Filtrar...`}
                        value={columnFilters[col] || ''}
                        autoFocus
                        onChange={e => handleColumnFilterChange(col, e.target.value)}
                        onKeyDown={e => handleColumnFilterKeyDown(col, e)}
                        onBlur={() => handleColumnFilterBlur(col)}
                        style={{ width: '100%', fontSize: '0.95em', padding: '2px 6px', borderRadius: 4, border: '1px solid #d1d5db' }}
                      />
                      <button
                        onClick={() => setOpenFilterCol(null)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: 2 }}
                        tabIndex={-1}
                        aria-label="Cerrar filtro"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </>
                  ) : (
                    <>
                      {formatoCampo(col)}
                      <button
                        className="filter-btn"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, marginLeft: 2 }}
                        onClick={() => setOpenFilterCol(col)}
                        tabIndex={-1}
                        aria-label={`Filtrar por ${formatoCampo(col)}`}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <circle cx="11" cy="11" r="7" stroke="#9ca3af" strokeWidth="2" />
                          <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" />
                        </svg>
                      </button>
                    </>
                  )}
                  <button
                    className={`sort-btn${sortConfig?.key === col ? ' active' : ''}`}
                    onClick={() => handleSort(col)}
                    tabIndex={-1}
                    style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, marginLeft: 2 }}
                    aria-label={`Ordenar por ${formatoCampo(col)}`}
                  >
                    {sortConfig?.key === col ? (
                      sortConfig.direction === 'asc' ? (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 15 12 9 18 15"/></svg>
                      ) : (
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                      )
                    ) : (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9ca3af" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 15 12 9 18 15"/></svg>
                    )}
                  </button>
                </span>
              </th>
            ))}
            {/* Elimina la columna de acciones */}
          </tr>
        </thead>
        <tbody>
          {cargando ? (
            <tr>
              <td colSpan={userRol === ROLES.ADMIN ? columns.length + 1 : columns.length}>Cargando registros...</td>
            </tr>
          ) : errorCarga ? (
            <tr>
              <td colSpan={userRol === ROLES.ADMIN ? columns.length + 1 : columns.length}>No se pudieron cargar los registros.</td>
            </tr>
          ) : registros.length === 0 ? (
            <tr>
              <td colSpan={userRol === ROLES.ADMIN ? columns.length + 1 : columns.length}>No hay registros disponibles.</td>
            </tr>
          ) : (
            registros.map((registro) => (
              <tr
                key={registro.id}
                className={menuRowId === registro.id ? 'selected' : ''}
                tabIndex={0}
                style={{ cursor: 'pointer', position: 'relative' }}
              >
                {userRol === ROLES.ADMIN && (
                  <td>
                    <input
                      type="checkbox"
                      checked={seleccionados.includes(registro.id)}
                      onChange={() => toggleSeleccion(registro.id)}
                    />
                  </td>
                )}
                {columns.map((col) => (
                  <td key={col} style={col === 'numero_inspector' ? { position: 'relative', textAlign: 'center' } : {}}>
                    {/* Si es la celda de numero_inspector, muestra el botón solo para admins */}
                    {col === 'numero_inspector' ? (
                      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                        {userRol === ROLES.ADMIN && (
                          <>
                            <button
                              className="action-menu-btn"
                              onClick={e => { setMenuRowId(registro.id); setMenuAnchor(e.currentTarget); }}
                              style={{ fontSize: 24, border: 'none', background: 'none', cursor: 'pointer', borderRadius: '50%', width: 36, height: 36, boxShadow: '0 2px 8px rgba(0,0,0,0.10)', backgroundColor: '#fff', color: '#0033A0', marginRight: 4 }}
                              aria-label="Acciones"
                            >
                              ⚙️
                            </button>
                            {/* Menú desplegable solo si el menú está abierto para esta fila */}
                            {menuAnchor && menuRowId === registro.id && (
                              <div
                                className="action-dropdown"
                                style={{
                                  position: 'absolute',
                                  top: 44,
                                  left: 0,
                                  minWidth: 140,
                                  background: 'linear-gradient(135deg, #e8efff 60%, #cce6ff 100%), linear-gradient(135deg, #0033A0 0%, #009FE3 100%)',
                                  backgroundBlendMode: 'lighten',
                                  borderRadius: 16,
                                  boxShadow: '0 8px 32px rgba(0,51,160,0.13), 0 2px 8px rgba(0,159,227,0.10)',
                                  padding: 0,
                                  zIndex: 1000,
                                  display: 'flex',
                                  flexDirection: 'column',
                                  overflow: 'hidden',
                                  border: 'none',
                                  animation: 'dropdownFadeIn 0.22s cubic-bezier(0.4,0,0.2,1)',
                                  backdropFilter: 'blur(8px) saturate(1.2)',
                                  WebkitBackdropFilter: 'blur(8px) saturate(1.2)'
                                }}
                                tabIndex={-1}
                                onBlur={handleCloseMenu}
                              >
                                <button className="dropdown-item" title="Editar" onClick={() => { handleEditClick(registro); handleCloseMenu(); }}>
                                  <FiEdit size={22} />
                                </button>
                                <button className="dropdown-item" title="Eliminar" onClick={() => { handleDelete(registro.id); handleCloseMenu(); }}>
                                  <FiTrash2 size={22} />
                                </button>
                                <button className="dropdown-item" title="Ver historial" onClick={() => { handleOpenModal(registro.numero_inspector); handleCloseMenu(); }}>
                                  <FiClock size={22} />
                                </button>
                              </div>
                            )}
                          </>
                        )}
                        <span>{registro[col as keyof Registro]}</span>
                      </span>
                    ) : (
                      registro[col as keyof Registro]
                    )}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
      </div>

      {/* Acciones en lote */}
      {userRol === ROLES.ADMIN && seleccionados.length > 0 && (
        <div className="acciones-lote">
          <button
            className="action-btn danger"
            onClick={handleEliminarSeleccion}
          >
            🗑 Eliminar selección
          </button>

          <button
            className="action-btn"
            onClick={exportarSeleccionComoCSV}
          >
            📥 Exportar selección
          </button>
        </div>
      )}

      <div className="paginacion">
        {/* Botón de ir al inicio */}
        <button
          onClick={() => setPagina(1)}
          disabled={pagina === 1}
          className="btn-paginacion"
        >
          &laquo;
        </button>
        {/* Renderizar páginas con saltos */}
        {Array.from({ length: totalPaginas }, (_, i) => i + 1)
          .filter(p =>
            p === 1 ||
            p === totalPaginas ||
            Math.abs(p - pagina) <= 2 ||
            (p === pagina - 3 && p > 1) ||
            (p === pagina + 3 && p < totalPaginas)
          )
          .reduce((acc, p, idx, arr) => {
            if (idx > 0 && p - arr[idx - 1] > 1) {
              acc.push('...');
            }
            acc.push(p);
            return acc;
          }, [] as (number | string)[])
          .map((p, idx) =>
            typeof p === 'string' ? (
              <span key={"ellipsis-" + idx} className="paginacion-ellipsis">{p}</span>
            ) : (
              <button
                key={p}
                onClick={() => setPagina(p as number)}
                className={p === pagina ? "btn-paginacion active" : "btn-paginacion"}
                disabled={p === pagina}
              >
                {p}
              </button>
            )
          )}
        {/* Botón de ir al final */}
        <button
          onClick={() => setPagina(totalPaginas)}
          disabled={pagina === totalPaginas}
          className="btn-paginacion"
        >
          &raquo;
        </button>
      </div>

      {isModalOpen && (
        <HistoryModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          historial={historial}
          inspectorId={selectedInspectorId}
        />
      )}

      <EditModal
        isOpen={editModalOpen}
        onClose={handleCloseEditModal}
        registro={registroParaEditar}
        onSuccess={handleEditSuccess}
      />

      <CreateModal
        isOpen={createModalOpen}
        onClose={handleCloseCreateModal}
        onCreated={handleCreateSuccess}
      />
        
        <BulkUploadModal
          isOpen={uploadModalOpen}
          onClose={handleCloseUploadModal}
          onUploaded={handleUploadSuccess}
        />

      <Notification
        message={notification.message}
        type={notification.type}
        show={notification.show}
        onClose={hideNotification}
        duration={5000}
      />

      <ConfirmModal
        isOpen={confirmModalVisible}
        mensaje={mensajeConfirmacion}
        onConfirm={handleConfirmacion}
        onCancel={cancelarEliminacion}
        titulo={tituloConfirmacion}
        tipo={tipoConfirmacion}
      />
    </div>
  );
}

export default RecordTable;

// ATENCIÓN: Este componente utiliza únicamente el endpoint '/upload_csv' para la carga masiva de registros.
// No usar '/registros/cargar'. El endpoint '/upload_csv' es el único que realiza validaciones estrictas y reemplazo total de datos.
// Si necesitas modificar la lógica de carga masiva, asegúrate de mantener este comportamiento.
import React, { useState, useRef } from "react";
import { useNotification } from "../hooks/useNotification";
import Notification from "./Notification";
import "./Modal.css";
import Papa from "papaparse";

interface BulkUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploaded: () => void;
}

function BulkUploadModal({ isOpen, onClose, onUploaded }: BulkUploadModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { notification, showSuccess, showError, hideNotification } = useNotification();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    
    if (!selected) {
      setFile(null);
      return;
    }

    // Validar tipo de archivo
    if (!selected.name.toLowerCase().endsWith('.csv')) {
      showError("Solo se permiten archivos CSV.");
      setFile(null);
      return;
    }

    // Validar tamaño (máximo 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (selected.size > maxSize) {
      showError("El archivo es demasiado grande. Máximo 10MB.");
      setFile(null);
      return;
    }

    setFile(selected);
    showSuccess("Archivo seleccionado correctamente.");
  };

  const handleUpload = async () => {
    if (!file) {
      showError("Selecciona un archivo CSV primero.");
      return;
    }

    // Validación de duplicados en 'Número de inspector'
    const text = await file.text();
    const parsed = Papa.parse(text, { header: true, skipEmptyLines: true });
    if (parsed.errors.length) {
      showError("Error al leer el archivo CSV. Verifica el formato.");
      return;
    }
    const rows = parsed.data;
    const seen = new Set();
    const duplicados = [];
    for (const row of rows as any[]) {
      const num = row["Número de inspector"];
      if (num !== undefined && num !== null && num !== "") {
        if (seen.has(num)) {
          duplicados.push(num);
        } else {
          seen.add(num);
        }
      }
    }
    if (duplicados.length > 0) {
      showError(`No se permite cargar el archivo porque hay valores duplicados en la columna 'Número de inspector': ${[...new Set(duplicados)].join(", ")}`);
      return;
    }

    // Validaciones por columna
    const erroresValidacion: any[] = [];
    const emailRegex = /^[\w\.-]+@[\w\.-]+\.\w+$/;
    const rowsFiltrados = (rows as any[]).filter(row => row['Número de inspector'] !== undefined && row['Número de inspector'] !== null && row['Número de inspector'] !== '');
    rowsFiltrados.forEach((row: any, idx: number) => {
      const fila = idx + 2;
      const numInspector = String(row['Número de inspector'] || '').trim();
      const celular = String(row['Celular'] || '').trim();
      const correo = String(row['Correo'] || '').trim();
      if (numInspector && !/^[0-9]+$/.test(numInspector)) {
        erroresValidacion.push({ fila, columna: 'Número de inspector', valor: numInspector, error: 'Debe ser numérico' });
      }
      if (celular && (!/^[0-9]{10}$/.test(celular))) {
        erroresValidacion.push({ fila, columna: 'Celular', valor: celular, error: 'Debe ser numérico de 10 dígitos' });
      }
      if (correo && !emailRegex.test(correo)) {
        erroresValidacion.push({ fila, columna: 'Correo', valor: correo, error: 'Debe ser un correo válido' });
      }
    });
    // Validación especial: 'Número de inspector' debe coincidir con el número después de 'ins' en 'Nombre'
    rowsFiltrados.forEach((row: any, idx: number) => {
      const fila = idx + 2;
      const numInspector = String(row['Número de inspector'] || '').trim();
      const nombre = String(row['Nombre'] || '').trim();
      if (/^[0-9]+$/.test(numInspector)) {
        if (numInspector.length === 1) {
          const patron1 = `ins${numInspector}`;
          const patron2 = `ins0${numInspector}`;
          if (!nombre.includes(patron1) && !nombre.includes(patron2)) {
            erroresValidacion.push({ fila, columna: 'Nombre', valor: nombre, error: `Debe contener 'ins${numInspector}' o 'ins0${numInspector}'` });
          }
        } else {
          const patron = `ins${numInspector}`;
          if (!nombre.includes(patron)) {
            erroresValidacion.push({ fila, columna: 'Nombre', valor: nombre, error: `Debe contener 'ins${numInspector}'` });
          }
        }
      }
    });
    if (erroresValidacion.length > 0) {
      showError('Errores de validación:\n' + erroresValidacion.map(e => `Fila ${e.fila} - ${e.columna}: ${e.valor} (${e.error})`).join('\n'));
      return;
    }

    setLoading(true);
    setUploadProgress(0);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append("file", file);

      // Simular progreso de carga
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/upload_csv`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Error al subir CSV");
      }

      const result = await res.json();
      showSuccess(`Archivo subido exitosamente. ${result.registros_creados || 0} registros procesados.`);
      setFile(null);
      onUploaded();
      onClose();
      
      // Limpiar input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error("Error al subir archivo CSV:", err);
      showError(err instanceof Error ? err.message : "Error al subir archivo CSV");
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFile(null);
      setUploadProgress(0);
      onClose();
      // Limpiar input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      // Crear un evento sintético que simule el evento de input
      const syntheticEvent = {
        target: { 
          files: [droppedFile],
          value: droppedFile.name
        }
      } as unknown as React.ChangeEvent<HTMLInputElement>;
      handleFileChange(syntheticEvent);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={handleClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Carga Masiva de Registros</h2>
            <button 
              className="modal-close" 
              onClick={handleClose}
              disabled={loading}
            >
              ×
            </button>
          </div>

          <div className="modal-form">
            <div className="upload-area"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="upload-content">
                <div className="upload-icon">📁</div>
                <h3>Selecciona un archivo CSV</h3>
                <p>Arrastra y suelta tu archivo aquí o haz clic para seleccionar</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  disabled={loading}
                  className="file-input"
                />
                <button 
                  type="button" 
                  className="btn-select-file"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                >
                  Seleccionar archivo
                </button>
              </div>
            </div>

            {file && (
              <div className="file-info">
                <div className="file-details">
                  <span className="file-name">📄 {file.name}</span>
                  <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                </div>
                <button 
                  type="button" 
                  className="btn-remove-file"
                  onClick={() => {
                    setFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                  disabled={loading}
                >
                  ✕
                </button>
              </div>
            )}

            {loading && (
              <div className="upload-progress">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <span className="progress-text">Subiendo archivo... {uploadProgress}%</span>
              </div>
            )}

            <div className="upload-instructions">
              <h4>Instrucciones:</h4>
              <ul>
                <li>El archivo debe estar en formato CSV</li>
                <li>Tamaño máximo: 10MB</li>
              </ul>
            </div>

            <div className="form-actions">
              <button 
                type="button" 
                onClick={handleClose} 
                className="btn-secondary"
                disabled={loading}
              >
                Cancelar
              </button>
              <button 
                type="button" 
                onClick={handleUpload}
                className="btn-primary"
                disabled={!file || loading}
              >
                {loading ? "Subiendo..." : "Subir CSV"}
              </button>
            </div>
          </div>
        </div>
      </div>

      <Notification
        message={notification.message}
        type={notification.type}
        show={notification.show}
        onClose={hideNotification}
        duration={5000}
      />
    </>
  );
}

export default BulkUploadModal; 
import React, { useState } from "react";
import { useNotification } from "../hooks/useNotification";
import { createRegistro } from "../services/recordService";
import Notification from "./Notification";
import "./Modal.css";

const campos = [
  "numero_inspector", "uuid", "nombre", "observaciones", "status", "region", "flota",
  "encargado", "celular", "correo", "direccion", "uso", "departamento",
  "ciudad", "tecnologia", "cmts_olt", "id_servicio", "mac_sn"
];

interface CreateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

interface FormData {
  [key: string]: string;
}

function CreateModal({ isOpen, onClose, onCreated }: CreateModalProps) {
  const [formData, setFormData] = useState<FormData>({});
  const [loading, setLoading] = useState(false);
  const { notification, showSuccess, showError, hideNotification } = useNotification();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await createRegistro(formData);
      showSuccess("Registro creado exitosamente");
      onCreated(); // Para recargar registros
      onClose();
      setFormData({}); // Limpiar formulario
    } catch (err) {
      console.error("Error al crear registro:", err);
      showError(err instanceof Error ? err.message : "Error al crear registro");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({});
      onClose();
    }
  };

  const formatFieldName = (field: string) => {
    return field
      .replace(/_/g, " ")
      .split(" ")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const getFieldType = (field: string) => {
    if (field === "correo") return "email";
    if (field === "celular") return "tel";
    if (field === "numero_inspector") return "number";
    // id_servicio debe ser texto
    return "text";
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="modal-overlay" onClick={handleClose}>
        <div className="modal-content wide" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Crear nuevo registro</h2>
            <button 
              className="modal-close" 
              onClick={handleClose}
              disabled={loading}
            >
              ×
            </button>
          </div>

          <form onSubmit={handleSubmit} className="modal-form">
            <div className="form-grid">
              {campos.map((campo) => (
                <div key={campo} className="form-group">
                  <label htmlFor={campo}>
                    {formatFieldName(campo)}
                    <span className="required">*</span>
                  </label>
                  <input
                    type={getFieldType(campo)}
                    id={campo}
                    name={campo}
                    value={formData[campo] || ""}
                    onChange={handleChange}
                    required
                    disabled={loading}
                    placeholder={`Ingrese ${formatFieldName(campo).toLowerCase()}`}
                  />
                </div>
              ))}
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
                type="submit" 
                className="btn-primary"
                disabled={loading}
              >
                {loading ? "Creando..." : "Crear Registro"}
              </button>
            </div>
          </form>
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

export default CreateModal; 
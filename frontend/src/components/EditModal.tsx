import React, { useState, useEffect } from "react";
import { updateRegistro } from "../services/recordService";
import { Registro, RegistroUpdate } from "../types/Registro";
import { useNotification } from "../hooks/useNotification";
import Notification from "./Notification";
import "./EditModal.css";

interface EditModalProps {
  isOpen: boolean;
  onClose: () => void;
  registro: Registro | null;
  onSuccess: () => void;
}

const EditModal: React.FC<EditModalProps> = ({ isOpen, onClose, registro, onSuccess }) => {
  const [form, setForm] = useState<RegistroUpdate>({});
  const [loading, setLoading] = useState(false);
  const { notification, showSuccess, showError, hideNotification } = useNotification();

  useEffect(() => {
    if (registro) {
      // Excluir el campo 'id' del formulario de edición
      const { id, ...registroSinId } = registro;
      setForm(registroSinId);
    }
  }, [registro]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!registro) return;

    setLoading(true);
    try {
      await updateRegistro(registro.id, form);
      showSuccess("Registro actualizado correctamente.");
      onSuccess();
      onClose();
    } catch (error) {
      console.error("Error al actualizar:", error);
      showError("Error al actualizar el registro. Intenta nuevamente.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    onClose();
  };

  if (!isOpen || !registro) return null;

  const campos = [
    { name: 'numero_inspector', label: 'N\u00famero Inspector', type: 'number' },
    { name: 'uuid', label: 'UUID', type: 'text' },
    { name: 'nombre', label: 'Nombre', type: 'text' },
    { name: 'observaciones', label: 'Observaciones', type: 'text' },
    { name: 'status', label: 'Status', type: 'text' },
    { name: 'region', label: 'Regi\u00f3n', type: 'text' },
    { name: 'flota', label: 'Flota', type: 'text' },
    { name: 'encargado', label: 'Encargado', type: 'text' },
    { name: 'celular', label: 'Celular', type: 'text' },
    { name: 'correo', label: 'Correo', type: 'email' },
    { name: 'direccion', label: 'Direcci\u00f3n', type: 'text' },
    { name: 'uso', label: 'Uso', type: 'text' },
    { name: 'departamento', label: 'Departamento', type: 'text' },
    { name: 'ciudad', label: 'Ciudad', type: 'text' },
    { name: 'tecnologia', label: 'Tecnolog\u00eda', type: 'text' },
    { name: 'cmts_olt', label: 'CMTS/OLT', type: 'text' },
    { name: 'id_servicio', label: 'ID Servicio', type: 'text' },
    { name: 'mac_sn', label: 'MAC/SN', type: 'text' },
  ];

  return (
    <>
      <div className="modal-backdrop" onClick={handleCancel}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h3>Editar Registro #{registro.id}</h3>
            <button className="modal-close" onClick={handleCancel}>
              ✕
            </button>
          </div>
          
          <form onSubmit={handleSubmit} className="edit-form">
            <div className="form-grid">
              {campos.map((campo) => (
                <div key={campo.name} className="form-field">
                  <label htmlFor={campo.name}>{campo.label}</label>
                  <input
                    type={campo.type}
                    id={campo.name}
                    name={campo.name}
                    value={form[campo.name as keyof RegistroUpdate] || ""}
                    onChange={handleChange}
                    required
                  />
                </div>
              ))}
            </div>
            
            <div className="modal-actions">
              <button 
                type="button" 
                onClick={handleCancel}
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
                {loading ? "Guardando..." : "Guardar Cambios"}
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
};

export default EditModal; 
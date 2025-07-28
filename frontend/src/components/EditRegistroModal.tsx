
import React, { useState, useEffect } from "react";
import "./Modal.css";
import { Registro, RegistroUpdate } from "../types/Registro";

interface Props {
  isOpen: boolean;
  registro: Registro | null;
  onClose: () => void;
  onUpdate: (registro: RegistroUpdate) => void;
}

const EditRegistroModal = ({ isOpen, registro, onClose, onUpdate }: Props) => {
  const [formData, setFormData] = useState<RegistroUpdate>({});

  useEffect(() => {
    if (registro) {
      setFormData({
        nombre: registro.nombre,
        status: registro.status,
        region: registro.region,
        ciudad: registro.ciudad,
      });
    }
  }, [registro]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onUpdate(formData);
    onClose();
  };

  if (!isOpen || !registro) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-box">
        <h2>Editar registro</h2>
        <input name="nombre" value={formData.nombre || ""} onChange={handleChange} placeholder="Nombre" />
        <input name="status" value={formData.status || ""} onChange={handleChange} placeholder="Status" />
        <input name="region" value={formData.region || ""} onChange={handleChange} placeholder="Región" />
        <input name="ciudad" value={formData.ciudad || ""} onChange={handleChange} placeholder="Ciudad" />
        <div className="modal-buttons">
          <button onClick={handleSubmit}>Guardar</button>
          <button onClick={onClose}>Cancelar</button>
        </div>
      </div>
    </div>
  );
};

export default EditRegistroModal;

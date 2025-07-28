
import React, { useState } from "react";
import Modal from "./Modal";
import { RegistroCreate } from "../types/Registro";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: RegistroCreate) => void;
}

const CreateRegistroModal = ({ isOpen, onClose, onCreate }: Props) => {
  const [form, setForm] = useState<RegistroCreate>({
    numero_inspector: 0,
    nombre: "",
    observaciones: "",
    status: "",
    region: "",
    flota: "",
    encargado: "",
    celular: "",
    correo: "",
    direccion: "",
    uso: "",
    departamento: "",
    ciudad: "",
    tecnologia: "",
    cmts_olt: "",
    id_servicio: "",
    mac_sn: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm({ 
      ...form, 
      [name]: name === 'numero_inspector' ? parseInt(value) || 0 : value 
    });
  };

  const handleSubmit = () => {
    onCreate(form);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Crear nuevo registro">
      <div className="form-grid">
        {Object.entries(form).map(([key, value]) => (
          <input
            key={key}
            name={key}
            type={key === 'numero_inspector' ? 'number' : 'text'}
            placeholder={key.replace(/_/g, " ")}
            value={value}
            onChange={handleChange}
          />
        ))}
      </div>
      <button onClick={handleSubmit}>Guardar</button>
    </Modal>
  );
};

export default CreateRegistroModal;

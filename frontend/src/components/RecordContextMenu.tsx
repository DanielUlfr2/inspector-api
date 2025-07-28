
import React from "react";
import "./RecordContextMenu.css";

interface Props {
  x: number;
  y: number;
  visible: boolean;
  onClose: () => void;
  onEditar: () => void;
  onEliminar: () => void;
  onHistorial: () => void;
}

const RecordContextMenu = ({ x, y, visible, onClose, onEditar, onEliminar, onHistorial }: Props) => {
  if (!visible) return null;

  return (
    <ul className="record-context-menu" style={{ top: y, left: x }} onClick={onClose}>
      <li onClick={onEditar}>Editar</li>
      <li onClick={onEliminar}>Eliminar</li>
      <li onClick={onHistorial}>Ver historial</li>
    </ul>
  );
};

export default RecordContextMenu;
    
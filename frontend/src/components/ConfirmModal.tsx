import React from "react";
import "./ConfirmModal.css";

interface ConfirmModalProps {
  mensaje: string;
  onConfirm: () => void;
  onCancel: () => void;
  isOpen: boolean;
  titulo?: string;
  tipo?: "danger" | "warning" | "info";
}

function ConfirmModal({ 
  mensaje, 
  onConfirm, 
  onCancel, 
  isOpen, 
  titulo = "Confirmar acción",
  tipo = "info"
}: ConfirmModalProps) {
  if (!isOpen) return null;

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onCancel();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Escape") {
      onCancel();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleOverlayClick} onKeyDown={handleKeyDown}>
      <div className={`confirm-modal ${tipo}`}>
        <div className="modal-header">
          <h3 className="modal-titulo">{titulo}</h3>
        </div>
        <div className="modal-body">
          <p className="modal-mensaje">{mensaje}</p>
        </div>
        <div className="confirm-buttons">
          <button className="btn cancel" onClick={onCancel}>
            Cancelar
          </button>
          <button className={`btn confirm ${tipo}`} onClick={onConfirm}>
            Confirmar
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal; 
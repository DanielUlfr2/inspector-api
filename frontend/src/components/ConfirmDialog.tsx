
import React from "react";
import "./ConfirmDialog.css";

interface Props {
  isOpen: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmDialog = ({ isOpen, message, onConfirm, onCancel }: Props) => {
  if (!isOpen) return null;

  return (
    <div className="confirm-overlay">
      <div className="confirm-box">
        <p>{message}</p>
        <div className="confirm-buttons">
          <button onClick={onConfirm} className="confirm-yes">Sí</button>
          <button onClick={onCancel} className="confirm-no">Cancelar</button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;

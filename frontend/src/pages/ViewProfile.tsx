import React from "react";
import { useUser } from "../context/UserContext";
import "./ViewProfile.css";

const ViewProfile: React.FC = () => {
  const { nombre, rol, token } = useUser();

  if (!nombre) {
    return (
      <div className="view-profile-container">
        <div className="view-profile-content">
          <p>No se pudo cargar la información del usuario.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="view-profile-container">
      
      <div className="view-profile-content">
        <div className="profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              <div className="avatar-initials">
                {nombre?.charAt(0).toUpperCase() || "U"}
              </div>
            </div>
            <div className="profile-info">
              <h2>{nombre}</h2>
              <p className="user-role">{rol}</p>
            </div>
          </div>

          <div className="profile-details">
            <div className="detail-section">
              <h3>Información del Usuario</h3>
              
              <div className="detail-item">
                <label>Nombre de usuario:</label>
                <span>{nombre}</span>
              </div>
              
              <div className="detail-item">
                <label>Rol:</label>
                <span className="role-badge">{rol}</span>
              </div>
              
              <div className="detail-item">
                <label>Estado de sesión:</label>
                <span>{token ? "Conectado" : "Desconectado"}</span>
              </div>
            </div>

            <div className="detail-section">
              <h3>Información del Sistema</h3>
              
              <div className="detail-item">
                <label>Estado de la cuenta:</label>
                <span className="status-active">Activa</span>
              </div>
              
              <div className="detail-item">
                <label>Último acceso:</label>
                <span>{new Date().toLocaleDateString('es-ES')}</span>
              </div>
            </div>

            <div className="profile-actions">
              <button
                className="btn-secondary"
                onClick={() => window.history.back()}
              >
                Volver
              </button>
              <button
                className="btn-primary"
                onClick={() => window.location.href = '/dashboard'}
              >
                Ir al Inventario
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewProfile; 
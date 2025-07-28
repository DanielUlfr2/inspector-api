import React, { useState } from "react";
import { useUser } from "../context/UserContext";
import { useNotification } from "../hooks/useNotification";
import Notification from "../components/Notification";
import "./EditProfile.css";

interface ProfileFormData {
  username: string;
  email: string;
}

const EditProfile: React.FC = () => {
  const { nombre, rol, updateUser } = useUser();
  const { notification, showSuccess, showError, hideNotification } = useNotification();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<ProfileFormData>({
    username: nombre || "",
    email: "",
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.username.trim()) {
      showError("El nombre de usuario es requerido");
      return;
    }

    if (!formData.email.trim()) {
      showError("El correo electrónico es requerido");
      return;
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      showError("Por favor ingresa un correo electrónico válido");
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/editar-perfil`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          nombre: formData.username,
          email: formData.email
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Actualizar el contexto del usuario
        if (updateUser) {
          updateUser({ ...data });
        }
        
        showSuccess("Perfil actualizado correctamente");
        
        // Cerrar modal automáticamente después de 1.5 segundos
        setTimeout(() => {
          window.history.back();
        }, 1500);
        
      } else {
        const errorData = await response.json();
        showError(errorData.detail || "Error al actualizar el perfil");
      }
      
    } catch (error) {
      console.error("Error al actualizar perfil:", error);
      showError("Error de conexión al actualizar el perfil");
    } finally {
      setLoading(false);
    }
  };

  if (!nombre) {
    return (
      <div className="edit-profile-container">
        <div className="edit-profile-content">
          <p>No se pudo cargar la información del usuario.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="edit-profile-container">
      
      <div className="edit-profile-content">
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

          <form onSubmit={handleSubmit} className="profile-form">
            <div className="form-section">
              <h3>Información Personal</h3>
              
              <div className="form-group">
                <label htmlFor="username">Nombre de usuario</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                  placeholder="Ingresa tu nombre de usuario"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Correo electrónico</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  disabled={loading}
                  placeholder="Ingresa tu correo electrónico"
                />
              </div>
            </div>

            <div className="form-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => window.history.back()}
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
        duration={3000}
      />
    </div>
  );
};

export default EditProfile; 
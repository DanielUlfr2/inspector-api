import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../hooks/useNotification';
import Notification from '../components/Notification';
import './ChangePassword.css';

function ChangePassword() {
  const navigate = useNavigate();
  const { notification, showSuccess, showError, hideNotification } = useNotification();
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const togglePasswordVisibility = (field: 'current' | 'new' | 'confirm') => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const validateForm = () => {
    if (!formData.currentPassword) {
      showError('Por favor ingresa tu contraseña actual');
      return false;
    }

    if (!formData.newPassword) {
      showError('Por favor ingresa la nueva contraseña');
      return false;
    }

    if (formData.newPassword.length < 8) {
      showError('La nueva contraseña debe tener al menos 8 caracteres');
      return false;
    }

    if (formData.newPassword === formData.currentPassword) {
      showError('La nueva contraseña debe ser diferente a la actual');
      return false;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      showError('Las contraseñas no coinciden');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/cambiar-contraseña`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          current_password: formData.currentPassword,
          new_password: formData.newPassword
        })
      });

      if (response.ok) {
        showSuccess('Contraseña actualizada correctamente');
        
        // Limpiar formulario
        setFormData({
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        });

        // Cerrar modal automáticamente después de 1.5 segundos
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        const errorData = await response.json();
        showError(errorData.detail || 'Error al cambiar la contraseña');
      }
    } catch (error) {
      console.error('Error al cambiar contraseña:', error);
      showError('Error de conexión al cambiar la contraseña');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  return (
    <div className="change-password-container">
      <div className="change-password-modal">
        <div className="modal-header">
          <h2>Cambiar Contraseña</h2>
          <button 
            className="close-button"
            onClick={handleCancel}
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="change-password-form">
          <div className="form-group">
            <label htmlFor="currentPassword">Contraseña actual</label>
            <div className="password-input-container">
              <input
                type={showPasswords.current ? 'text' : 'password'}
                id="currentPassword"
                name="currentPassword"
                value={formData.currentPassword}
                onChange={handleInputChange}
                className="password-input"
                placeholder="Ingresa tu contraseña actual"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => togglePasswordVisibility('current')}
                aria-label={showPasswords.current ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPasswords.current ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="newPassword">Nueva contraseña</label>
            <div className="password-input-container">
              <input
                type={showPasswords.new ? 'text' : 'password'}
                id="newPassword"
                name="newPassword"
                value={formData.newPassword}
                onChange={handleInputChange}
                className="password-input"
                placeholder="Ingresa la nueva contraseña"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => togglePasswordVisibility('new')}
                aria-label={showPasswords.new ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPasswords.new ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmar nueva contraseña</label>
            <div className="password-input-container">
              <input
                type={showPasswords.confirm ? 'text' : 'password'}
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="password-input"
                placeholder="Confirma la nueva contraseña"
                required
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => togglePasswordVisibility('confirm')}
                aria-label={showPasswords.confirm ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              >
                {showPasswords.confirm ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
          </div>

          <div className="password-requirements">
            <p><strong>Requisitos de la nueva contraseña:</strong></p>
            <ul>
              <li>Mínimo 8 caracteres</li>
              <li>Debe ser diferente a la contraseña actual</li>
              <li>Se recomienda incluir mayúsculas, minúsculas, números y símbolos</li>
            </ul>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={handleCancel}
              className="cancel-button"
              disabled={isLoading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="save-button"
              disabled={isLoading}
            >
              {isLoading ? 'Guardando...' : 'Cambiar contraseña'}
            </button>
          </div>
        </form>
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
}

export default ChangePassword; 
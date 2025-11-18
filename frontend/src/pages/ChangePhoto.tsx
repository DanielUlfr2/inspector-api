import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { useNotification } from '../hooks/useNotification';
import { getImageUrl } from '../utils/imageUtils';
import Notification from '../components/Notification';
import './ChangePhoto.css';

function ChangePhoto() {
  const { id, nombre, foto, updateUser } = useUser();
  const navigate = useNavigate();
  const { notification, showSuccess, showError, hideNotification } = useNotification();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validar tipo de archivo
      if (!file.type.startsWith('image/')) {
        showError('Por favor selecciona un archivo de imagen válido');
        return;
      }

      // Validar tamaño (máximo 5MB)
      if (file.size > 5 * 1024 * 1024) {
        showError('La imagen debe ser menor a 5MB');
        return;
      }

      setSelectedFile(file);
      
      // Crear preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!selectedFile) {
      showError('Por favor selecciona una imagen');
      return;
    }

    setIsLoading(true);

    try {
      const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true' || import.meta.env.MODE === 'demo';
      
      // Obtener el ID del usuario del contexto
      if (!id) {
        showError('No se pudo obtener la información del usuario. Por favor, inicia sesión nuevamente.');
        return;
      }

      let response: Response;
      
      if (isDemoMode) {
        // Simular delay y respuesta en modo demo
        await new Promise(resolve => setTimeout(resolve, 500));
        response = new Response(
          JSON.stringify({
            message: "Foto actualizada correctamente (demo)",
            foto: `/static/fotos/demo_${id}.jpg`
          }),
          { status: 200 }
        );
      } else {
        const formData = new FormData();
        formData.append('file', selectedFile);

        response = await fetch(`${import.meta.env.VITE_API_URL}/usuarios/${id}/foto`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: formData
        });
      }

      if (response.ok) {
        const data = await response.json();
        
        // Actualizar el contexto del usuario con la nueva foto
        if (updateUser) {
          updateUser({ foto: data.foto });
        }
        
        showSuccess('Foto de perfil actualizada correctamente');
        
        // Cerrar modal automáticamente después de 1.5 segundos
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } else {
        const errorData = await response.json();
        showError(errorData.detail || 'Error al actualizar la foto de perfil');
      }
    } catch (error) {
      console.error('Error al cambiar foto:', error);
      showError('Error de conexión al actualizar la foto');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/dashboard');
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="change-photo-container">
      <div className="change-photo-modal">
        <div className="modal-header">
          <h2>Cambiar Foto de Perfil</h2>
          <button 
            className="close-button"
            onClick={handleCancel}
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="change-photo-form">
          <div className="photo-preview-section">
            <div className="current-photo">
              <h3>Foto actual:</h3>
              <div className="avatar-container">
                {foto ? (
                  <img
                    src={getImageUrl(foto) || ''}
                    alt="Foto actual"
                    className="current-avatar"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.style.display = 'none';
                      const initialsDiv = target.nextElementSibling as HTMLElement;
                      if (initialsDiv) {
                        initialsDiv.style.display = 'flex';
                      }
                    }}
                  />
                ) : null}
                <div className="avatar-initials">
                  {getInitials(nombre || "Usuario")}
                </div>
              </div>
            </div>

            {preview && (
              <div className="new-photo">
                <h3>Nueva foto:</h3>
                <div className="avatar-container">
                  <img
                    src={preview}
                    alt="Vista previa"
                    className="preview-avatar"
                  />
                </div>
              </div>
            )}
          </div>

          <div className="file-input-section">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="file-input"
              id="photo-input"
            />
            <button
              type="button"
              onClick={triggerFileInput}
              className="select-file-button"
            >
              {selectedFile ? 'Cambiar imagen' : 'Seleccionar imagen'}
            </button>
            {selectedFile && (
              <p className="file-info">
                Archivo seleccionado: {selectedFile.name}
              </p>
            )}
          </div>

          <div className="form-requirements">
            <p><strong>Requisitos:</strong></p>
            <ul>
              <li>Formatos permitidos: JPG, PNG, GIF</li>
              <li>Tamaño máximo: 5MB</li>
              <li>Resolución recomendada: 200x200 píxeles o superior</li>
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
              disabled={!selectedFile || isLoading}
            >
              {isLoading ? 'Guardando...' : 'Guardar cambios'}
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

export default ChangePhoto; 
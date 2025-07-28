import React, { useState, useEffect, useRef } from "react";
import { useUser } from "../context/UserContext";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../hooks/useNotification";
import Notification from "./Notification";
import "./UserMenu.css";
import { apiGet } from "../services/apiClient";
import { FiHome } from "react-icons/fi";

function UserMenu() {
  const { nombre, rol, foto, logout } = useUser();
  const [menuAbierto, setMenuAbierto] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { notification, showSuccess, hideNotification } = useNotification();

  if (!nombre) return null;

  // Cerrar menú al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuAbierto(false);
      }
    };

    if (menuAbierto) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuAbierto]);

  // Cerrar menú con Escape
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMenuAbierto(false);
      }
    };

    if (menuAbierto) {
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [menuAbierto]);

  const toggleMenu = () => {
    setMenuAbierto(!menuAbierto);
  };

  const handleLogout = () => {
    try {
      logout();
      showSuccess("Sesión cerrada correctamente");
      navigate("/");
    } catch (error) {
      console.error("Error al cerrar sesión:", error);
    }
  };

  const handleEditProfile = () => {
    setMenuAbierto(false);
    navigate("/editar-perfil");
  };

  const handleChangePassword = () => {
    setMenuAbierto(false);
    navigate("/cambiar-contraseña");
  };

  const handleChangePhoto = () => {
    setMenuAbierto(false);
    navigate("/cambiar-foto");
  };

  const handleDashboard = () => {
    setMenuAbierto(false);
    navigate("/dashboard");
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarSrc = () => {
    // Si el usuario tiene una foto de perfil, usarla
    if (foto) {
      return foto;
    }
    // Si no, usar placeholder SVG
    return "/default-avatar.svg";
  };

  // Función para exportar historial global
  const exportarHistorialGlobal = async () => {
    try {
      const data = await apiGet("/historial-cambios/exportar");
      const dataStr = JSON.stringify(data, null, 2);
      const blob = new Blob([dataStr], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `historial_cambios_global.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      alert("Error al exportar historial global");
    }
  };

  return (
    <>
      <div className="user-menu" ref={menuRef}>
        <div 
          className="menu-header" 
          onClick={toggleMenu}
          role="button"
          tabIndex={0}
          aria-label="Abrir menú de usuario"
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              toggleMenu();
            }
          }}
        >
          <div className="avatar-container">
            <img
              src={getAvatarSrc()}
              alt="Foto de perfil"
              className="avatar"
              onError={(e) => {
                // Si la imagen falla, mostrar iniciales
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
                const initialsDiv = target.nextElementSibling as HTMLElement;
                if (initialsDiv) {
                  initialsDiv.style.display = 'flex';
                }
              }}
            />
            <div className="avatar-initials">
              {getInitials(nombre || "Usuario")}
            </div>
          </div>
          
          <div className="user-info">
            <span className="user-name">{nombre || "Usuario"}</span>
            <span className="user-role">{rol || "Usuario"}</span>
          </div>
          
          <span className={`hamburger-icon ${menuAbierto ? 'active' : ''}`}>
            ☰
          </span>
        </div>

        {menuAbierto && (
          <div className="menu-opciones" role="menu">
            <div className="menu-section">
              <button 
                onClick={handleDashboard}
                className="menu-item"
                role="menuitem"
              >
                <FiHome size={16} />
                Inventario
              </button>
              
              <button 
                onClick={handleEditProfile}
                className="menu-item"
                role="menuitem"
              >
                <span className="menu-icon">👤</span>
                Editar perfil
              </button>

              <button 
                onClick={handleChangePassword}
                className="menu-item"
                role="menuitem"
              >
                <span className="menu-icon">🔒</span>
                Cambiar contraseña
              </button>

              <button 
                onClick={handleChangePhoto}
                className="menu-item"
                role="menuitem"
              >
                <span className="menu-icon">📷</span>
                Cambiar foto de perfil
              </button>
            </div>
            
            <div className="menu-divider"></div>
            
            <div className="menu-section">
              <button 
                onClick={handleLogout}
                className="menu-item menu-item-danger"
                role="menuitem"
              >
                <span className="menu-icon">🚪</span>
                Cerrar sesión
              </button>
              <button
                onClick={exportarHistorialGlobal}
                className="menu-item"
                role="menuitem"
              >
                <span className="menu-icon">📥</span>
                Exportar historial de cambios
              </button>
            </div>
          </div>
        )}
      </div>

      <Notification
        message={notification.message}
        type={notification.type}
        show={notification.show}
        onClose={hideNotification}
        duration={3000}
      />
    </>
  );
}

export default UserMenu; 
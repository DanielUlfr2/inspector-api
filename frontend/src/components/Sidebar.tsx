import React, { useState, useEffect, useRef } from "react";
import { useUser } from "../context/UserContext";
import { getImageUrl } from "../utils/imageUtils";
import { getTotalRegistros } from "../services/recordService";
import { useNavigate } from "react-router-dom";
import { FiHome, FiUsers, FiClock, FiUser, FiEdit, FiRefreshCw, FiLogOut, FiImage } from "react-icons/fi";
import UserManagementModal from "./UserManagementModal";
import "./Sidebar.css";

function Sidebar() {
  const { nombre, rol, foto, logout } = useUser();
  const [submenuOpen, setSubmenuOpen] = useState(false);
  const [isSidebarVisible, setIsSidebarVisible] = useState(false);
  const [isTinyScreen, setIsTinyScreen] = useState(false);
  const [showUserManagement, setShowUserManagement] = useState(false);
  const sidebarRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();
  const isAdmin = rol === "admin";

  useEffect(() => {
    const handleResize = () => setIsTinyScreen(window.innerWidth <= 500);
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Ocultar sidebar al hacer click fuera
  useEffect(() => {
    if (!isSidebarVisible) return;
    function handleClick(e: MouseEvent) {
      if (sidebarRef.current && !(sidebarRef.current as HTMLDivElement).contains(e.target as Node)) {
        setIsSidebarVisible(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [isSidebarVisible]);

  if (isTinyScreen) return null;

  // Notifica al body si el sidebar está visible para adaptar el layout
  useEffect(() => {
    if (isSidebarVisible) {
      document.body.classList.add('sidebar-ig-visible');
    } else {
      document.body.classList.remove('sidebar-ig-visible');
    }
    return () => document.body.classList.remove('sidebar-ig-visible');
  }, [isSidebarVisible]);

  return (
    <>
      {/* Hotspot invisible para mostrar el sidebar al hacer hover */}
      <div
        className="sidebar-hotspot"
        onMouseEnter={() => setIsSidebarVisible(true)}
        style={{ position: 'fixed', top: 0, left: 0, width: 16, height: '100vh', zIndex: 101 }}
      />
      <aside
        className={`sidebar-ig-tigo ${isSidebarVisible ? 'visible' : ''}`}
        ref={sidebarRef}
        onMouseLeave={() => setIsSidebarVisible(false)}
        style={{ left: isSidebarVisible ? 0 : -90 }}
      >
        <div className="sidebar-ig-avatar">
          <div className="avatar">
            {foto ? (
              <img
                src={getImageUrl(foto) || ''}
                alt="Foto de perfil"
                className="avatar-img"
              />
            ) : (
              <div className="avatar-iniciales">
                {(nombre || "U").charAt(0).toUpperCase()}
              </div>
            )}
          </div>
        </div>
        <nav className="sidebar-ig-nav">
          <ul>
            <li>
              <a href="#" title="Inventario" onClick={e => { e.preventDefault(); navigate("/dashboard"); }}>
                <FiHome size={26} />
              </a>
            </li>
            <li>
              <a href="#" title="Imágenes" onClick={e => { e.preventDefault(); navigate("/imagenes"); }}>
                <FiImage size={26} />
              </a>
            </li>
            {isAdmin && (
              <li>
                <a href="#" title="Gestión de usuarios" onClick={e => { e.preventDefault(); setShowUserManagement(true); }}>
                  <FiUsers size={26} />
                </a>
              </li>
            )}
          </ul>
        </nav>
        <div className="sidebar-ig-actions">
          <button className="sidebar-ig-btn" title="Editar perfil" onClick={() => setSubmenuOpen((v) => !v)}>
            <FiEdit size={22} />
          </button>
          <button className="sidebar-ig-btn" title="Recontar registros" onClick={async () => {
            try {
              const res = await getTotalRegistros();
              alert(`Total de registros: ${res.total}`);
            } catch (e) {
              alert("Error al obtener el total de registros");
            }
          }}>
            <FiRefreshCw size={22} />
          </button>
          <button className="sidebar-ig-btn" title="Cerrar sesión" onClick={logout}>
            <FiLogOut size={22} />
          </button>
        </div>
        {submenuOpen && (
          <div className="sidebar-ig-submenu">
            <button className="submenu-item" onClick={() => { setSubmenuOpen(false); navigate("/editar-perfil"); }}><FiUser /> Editar información</button>
            <button className="submenu-item" onClick={() => { setSubmenuOpen(false); navigate("/cambiar-contraseña"); }}><FiEdit /> Cambiar contraseña</button>
            <button className="submenu-item" onClick={() => { setSubmenuOpen(false); navigate("/cambiar-foto"); }}><FiUser /> Cambiar foto</button>
          </div>
        )}
      </aside>
      {showUserManagement && (
        <UserManagementModal onClose={() => setShowUserManagement(false)} />
      )}
    </>
  );
}

export default Sidebar; 
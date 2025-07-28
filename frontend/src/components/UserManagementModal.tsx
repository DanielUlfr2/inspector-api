import React, { useEffect, useState } from "react";
import { getUsers, deleteUser, createUser, updateUser, resetUserPassword, toggleUserActive, getUserHistory } from "../services/userService";
import { useUser } from "../context/UserContext";
import Toast from "./Toast";
import "../styles/modal.css";

interface UserManagementModalProps {
  onClose: () => void;
}

interface Usuario {
  id: number;
  username: string;
  email: string;
  rol: string;
  activo: boolean;
  foto?: string | null;
}

interface HistorialItem {
  id: number;
  usuario_id: number;
  fecha: string;
  admin_que_realizo_cambio: string;
  accion: string;
  campo?: string;
  valor_anterior?: string;
  valor_nuevo?: string;
  descripcion?: string;
}

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const UserManagementModal: React.FC<UserManagementModalProps> = ({ onClose }) => {
  const { id } = useUser();
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [updating, setUpdating] = useState(false);
  const [toast, setToast] = useState<{ message: string; type?: "success" | "error" | "info" } | null>(null);
  const [historialVisible, setHistorialVisible] = useState(false);
  const [historialUsuario, setHistorialUsuario] = useState<HistorialItem[]>([]);
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState<Usuario | null>(null);

  const [newUser, setNewUser] = useState({
    username: "",
    email: "",
    password: "",
    rol: "user"
  });

  const [editUser, setEditUser] = useState({
    username: "",
    email: "",
    rol: "user"
  });

  const currentUserId = id;

  const showToast = (message: string, type: "success" | "error" | "info" = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  const fetchUsuarios = async () => {
    try {
      setLoading(true);
      const data = await getUsers();
      setUsuarios(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || "Error al cargar usuarios");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsuarios();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("¿Estás seguro de que quieres eliminar este usuario?")) return;
    
    try {
      await deleteUser(id);
      setUsuarios(usuarios.filter(u => u.id !== id));
      showToast("Usuario eliminado correctamente", "success");
    } catch (err: any) {
      showToast(err.message || "Error al eliminar usuario", "error");
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!emailRegex.test(newUser.email)) {
      showToast("Email inválido", "error");
      return;
    }
    
    if (newUser.password.length < 8) {
      showToast("La contraseña debe tener al menos 8 caracteres", "error");
      return;
    }
    
    if (newUser.username.length < 3) {
      showToast("El nombre de usuario debe tener al menos 3 caracteres", "error");
      return;
    }
    
    try {
      setCreating(true);
      const created = await createUser(newUser);
      setUsuarios([...usuarios, created]);
      setNewUser({ username: "", email: "", password: "", rol: "user" });
      setShowCreate(false);
      showToast("Usuario creado correctamente", "success");
    } catch (err: any) {
      showToast(err.message || "Error al crear usuario", "error");
    } finally {
      setCreating(false);
    }
  };

  const handleEditClick = (usuario: Usuario) => {
    setEditId(usuario.id);
    setEditUser({
      username: usuario.username,
      email: usuario.email,
      rol: usuario.rol
    });
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setEditUser({
      ...editUser,
      [e.target.name]: e.target.value
    });
  };

  const handleEditSave = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    
    console.log("Iniciando edición de usuario:", { editId, editUser });
    
    if (!emailRegex.test(editUser.email)) {
      showToast("Email inválido", "error");
      return;
    }
    
    if (editUser.username.length < 3) {
      showToast("El nombre de usuario debe tener al menos 3 caracteres", "error");
      return;
    }
    
    try {
      setUpdating(true);
      console.log("Enviando petición de actualización:", { id: editId, data: editUser });
      const updated = await updateUser(editId!, editUser);
      console.log("Respuesta del servidor:", updated);
      setUsuarios(usuarios.map(u => u.id === editId ? updated : u));
      setEditId(null);
      showToast("Usuario actualizado correctamente", "success");
    } catch (err: any) {
      console.error("Error al actualizar usuario:", err);
      showToast(err.message || "Error al actualizar usuario", "error");
    } finally {
      setUpdating(false);
    }
  };

  const handleEditCancel = () => {
    setEditId(null);
  };

  const handleResetPassword = async (usuario: Usuario) => {
    const newPassword = prompt(`Ingresa la nueva contraseña para ${usuario.username}:`);
    if (!newPassword) return;
    
    if (newPassword.length < 8) {
      showToast("La contraseña debe tener al menos 8 caracteres", "error");
      return;
    }
    
    try {
      await resetUserPassword(usuario.id, newPassword);
      showToast("Contraseña restablecida correctamente", "success");
    } catch (err: any) {
      showToast(err.message || "Error al restablecer contraseña", "error");
    }
  };

  const handleToggleActive = async (usuario: Usuario) => {
    try {
      const updated = await toggleUserActive(usuario.id);
      setUsuarios(usuarios.map(u => u.id === usuario.id ? updated : u));
      showToast(`Usuario ${updated.activo ? 'activado' : 'deshabilitado'} correctamente`, "success");
    } catch (err: any) {
      showToast(err.message || "Error al cambiar estado del usuario", "error");
    }
  };

  const handleViewHistory = async (usuario: Usuario) => {
    try {
      const historial = await getUserHistory(usuario.id);
      setHistorialUsuario(historial);
      setUsuarioSeleccionado(usuario);
      setHistorialVisible(true);
    } catch (err: any) {
      showToast(err.message || "Error al cargar historial", "error");
    }
  };

  const formatFecha = (fecha: string) => {
    return new Date(fecha).toLocaleString('es-ES');
  };

  const getAccionText = (accion: string) => {
    const acciones: { [key: string]: string } = {
      'creacion': 'Creación',
      'edicion': 'Edición',
      'activacion': 'Activación',
      'desactivacion': 'Desactivación',
      'eliminacion': 'Eliminación',
      'restablecer_password': 'Restablecer contraseña'
    };
    return acciones[accion] || accion;
  };

  return (
    <>
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <div className="modal-header">
            <h2>Gestión de Usuarios</h2>
            <button className="modal-close" onClick={onClose}>×</button>
          </div>
          <div className="modal-body">
            <p style={{ marginBottom: "1rem", color: "#666" }}>
              Aquí podrás ver, crear, editar y eliminar usuarios.
            </p>
            
            <button 
              onClick={() => setShowCreate(v => !v)} 
              style={{ 
                marginBottom: "1rem",
                padding: "0.5rem 1rem",
                backgroundColor: "#003DA5",
                color: "white",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "0.9rem"
              }}
            >
              {showCreate ? "Cancelar" : "Crear nuevo usuario"}
            </button>
            
            {showCreate && (
              <form onSubmit={handleCreate} style={{ 
                marginBottom: "1.5rem", 
                background: "#f8f9fa", 
                padding: "1rem", 
                borderRadius: "12px",
                border: "1px solid #e9ecef"
              }}>
                <div style={{ 
                  display: "grid", 
                  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", 
                  gap: "0.75rem",
                  alignItems: "end"
                }}>
                  <div>
                    <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.9rem", fontWeight: "500" }}>
                      Nombre de usuario
                    </label>
                    <input
                      required
                      placeholder="Usuario"
                      value={newUser.username}
                      onChange={e => setNewUser({ ...newUser, username: e.target.value })}
                      style={{ 
                        width: "100%",
                        padding: "0.5rem",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        fontSize: "0.9rem"
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.9rem", fontWeight: "500" }}>
                      Email
                    </label>
                    <input
                      required
                      type="email"
                      placeholder="email@ejemplo.com"
                      value={newUser.email}
                      onChange={e => setNewUser({ ...newUser, email: e.target.value })}
                      style={{ 
                        width: "100%",
                        padding: "0.5rem",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        fontSize: "0.9rem"
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.9rem", fontWeight: "500" }}>
                      Contraseña
                    </label>
                    <input
                      required
                      type="password"
                      placeholder="Mínimo 8 caracteres"
                      value={newUser.password}
                      onChange={e => setNewUser({ ...newUser, password: e.target.value })}
                      style={{ 
                        width: "100%",
                        padding: "0.5rem",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        fontSize: "0.9rem"
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: "block", marginBottom: "0.25rem", fontSize: "0.9rem", fontWeight: "500" }}>
                      Rol
                    </label>
                    <select
                      value={newUser.rol}
                      onChange={e => setNewUser({ ...newUser, rol: e.target.value })}
                      style={{ 
                        width: "100%",
                        padding: "0.5rem",
                        border: "1px solid #ddd",
                        borderRadius: "6px",
                        fontSize: "0.9rem"
                      }}
                    >
                      <option value="user">Usuario</option>
                      <option value="admin">Administrador</option>
                    </select>
                  </div>
                  <div>
                    <button 
                      type="submit" 
                      disabled={creating} 
                      style={{ 
                        width: "100%",
                        padding: "0.5rem",
                        backgroundColor: creating ? "#6c757d" : "#28a745",
                        color: "white",
                        border: "none",
                        borderRadius: "6px",
                        cursor: creating ? "not-allowed" : "pointer",
                        fontSize: "0.9rem"
                      }}
                    >
                      {creating ? "Creando..." : "Crear usuario"}
                    </button>
                  </div>
                </div>
              </form>
            )}
            
            {loading ? (
              <div style={{ textAlign: "center", padding: "2rem" }}>
                <p>Cargando usuarios...</p>
              </div>
            ) : error ? (
              <div style={{ 
                background: "#f8d7da", 
                color: "#721c24", 
                padding: "0.75rem", 
                borderRadius: "6px",
                border: "1px solid #f5c6cb"
              }}>
                {error}
              </div>
            ) : (
              <div style={{ overflowX: "auto" }}>
                <table style={{ 
                  width: "100%", 
                  borderCollapse: "collapse", 
                  marginTop: "1rem",
                  minWidth: "800px",
                  fontSize: "0.9rem"
                }}>
                  <thead>
                    <tr style={{ backgroundColor: "#f8f9fa" }}>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Nombre
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Email
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Rol
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Estado
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {usuarios.map(usuario => (
                      <tr key={usuario.id} style={{ 
                        opacity: usuario.activo ? 1 : 0.6, 
                        backgroundColor: usuario.activo ? 'transparent' : '#f8f9fa',
                        borderBottom: "1px solid #dee2e6"
                      }}>
                        {editId === usuario.id ? (
                          <>
                            <td style={{ padding: "0.5rem" }}>
                              <input
                                name="username"
                                value={editUser.username}
                                onChange={handleEditChange}
                                style={{ 
                                  width: "100%",
                                  padding: "0.25rem",
                                  border: "1px solid #ddd",
                                  borderRadius: "4px",
                                  fontSize: "0.9rem"
                                }}
                                required
                              />
                            </td>
                            <td style={{ padding: "0.5rem" }}>
                              <input
                                name="email"
                                type="email"
                                value={editUser.email}
                                onChange={handleEditChange}
                                style={{ 
                                  width: "100%",
                                  padding: "0.25rem",
                                  border: "1px solid #ddd",
                                  borderRadius: "4px",
                                  fontSize: "0.9rem"
                                }}
                                required
                              />
                            </td>
                            <td style={{ padding: "0.5rem" }}>
                              <select
                                name="rol"
                                value={editUser.rol}
                                onChange={handleEditChange}
                                style={{ 
                                  width: "100%",
                                  padding: "0.25rem",
                                  border: "1px solid #ddd",
                                  borderRadius: "4px",
                                  fontSize: "0.9rem"
                                }}
                              >
                                <option value="user">Usuario</option>
                                <option value="admin">Administrador</option>
                              </select>
                            </td>
                            <td style={{ padding: "0.5rem" }}>
                              <span style={{ 
                                padding: "0.25rem 0.5rem", 
                                borderRadius: "4px", 
                                fontSize: "0.8rem",
                                backgroundColor: usuario.activo ? "#d4edda" : "#f8d7da",
                                color: usuario.activo ? "#155724" : "#721c24"
                              }}>
                                {usuario.activo ? "Activo" : "Deshabilitado"}
                              </span>
                            </td>
                            <td style={{ padding: "0.5rem" }}>
                              <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                                <button 
                                  type="button"
                                  onClick={handleEditSave}
                                  disabled={updating} 
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: updating ? "#6c757d" : "#28a745",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: updating ? "not-allowed" : "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  {updating ? "Guardando..." : "Guardar"}
                                </button>
                                <button 
                                  type="button" 
                                  onClick={handleEditCancel}
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: "#6c757d",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  Cancelar
                                </button>
                              </div>
                            </td>
                          </>
                        ) : (
                          <>
                            <td style={{ padding: "0.5rem", fontWeight: "500" }}>{usuario.username}</td>
                            <td style={{ padding: "0.5rem" }}>{usuario.email}</td>
                            <td style={{ padding: "0.5rem" }}>
                              <span style={{ 
                                padding: "0.25rem 0.5rem", 
                                borderRadius: "4px", 
                                fontSize: "0.8rem",
                                backgroundColor: usuario.rol === "admin" ? "#cce5ff" : "#e2e3e5",
                                color: usuario.rol === "admin" ? "#004085" : "#383d41"
                              }}>
                                {usuario.rol === "admin" ? "Administrador" : "Usuario"}
                              </span>
                            </td>
                            <td style={{ padding: "0.5rem" }}>
                              <span style={{ 
                                padding: "0.25rem 0.5rem", 
                                borderRadius: "4px", 
                                fontSize: "0.8rem",
                                backgroundColor: usuario.activo ? "#d4edda" : "#f8d7da",
                                color: usuario.activo ? "#155724" : "#721c24"
                              }}>
                                {usuario.activo ? "Activo" : "Deshabilitado"}
                              </span>
                            </td>
                            <td style={{ padding: "0.5rem" }}>
                              <div style={{ display: "flex", gap: "0.25rem", flexWrap: "wrap" }}>
                                <button 
                                  onClick={() => handleEditClick(usuario)}
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: "#007bff",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  Editar
                                </button>
                                <button
                                  onClick={() => handleDelete(usuario.id)}
                                  disabled={usuario.id === currentUserId}
                                  title={usuario.id === currentUserId ? "No puedes eliminar tu propio usuario" : "Eliminar"}
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: usuario.id === currentUserId ? "#6c757d" : "#dc3545",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: usuario.id === currentUserId ? "not-allowed" : "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  Eliminar
                                </button>
                                <button
                                  onClick={() => handleResetPassword(usuario)}
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: "#ffc107",
                                    color: "#212529",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  Restablecer contraseña
                                </button>
                                <button
                                  onClick={() => handleToggleActive(usuario)}
                                  disabled={usuario.id === currentUserId}
                                  title={usuario.id === currentUserId ? "No puedes deshabilitar tu propio usuario" : usuario.activo ? "Deshabilitar" : "Activar"}
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: usuario.id === currentUserId ? "#6c757d" : (usuario.activo ? "#dc3545" : "#28a745"),
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: usuario.id === currentUserId ? "not-allowed" : "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  {usuario.activo ? "Deshabilitar" : "Activar"}
                                </button>
                                <button
                                  onClick={() => handleViewHistory(usuario)}
                                  style={{ 
                                    padding: "0.25rem 0.5rem",
                                    backgroundColor: "#17a2b8",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "4px",
                                    cursor: "pointer",
                                    fontSize: "0.8rem"
                                  }}
                                >
                                  Ver historial
                                </button>
                              </div>
                            </td>
                          </>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modal de historial */}
      {historialVisible && (
        <div className="modal-overlay" onClick={() => setHistorialVisible(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Historial de cambios - {usuarioSeleccionado?.username}</h2>
              <button className="modal-close" onClick={() => setHistorialVisible(false)}>×</button>
            </div>
            <div className="modal-body">
              {historialUsuario.length === 0 ? (
                <p style={{ textAlign: "center", color: "#666" }}>
                  No hay historial de cambios para este usuario.
                </p>
              ) : (
                <div style={{ overflowX: "auto" }}>
                  <table style={{ 
                    width: "100%", 
                    borderCollapse: "collapse", 
                    marginTop: "1rem",
                    fontSize: "0.9rem"
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: "#f8f9fa" }}>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Fecha
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Acción
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Admin
                      </th>
                      <th style={{ 
                        borderBottom: "2px solid #dee2e6", 
                        textAlign: "left", 
                        padding: "0.75rem 0.5rem",
                        fontWeight: "600"
                      }}>
                        Detalles
                      </th>
                    </tr>
                    </thead>
                    <tbody>
                      {historialUsuario.map(item => (
                        <tr key={item.id} style={{ borderBottom: "1px solid #dee2e6" }}>
                          <td style={{ padding: "0.5rem" }}>{formatFecha(item.fecha)}</td>
                          <td style={{ padding: "0.5rem" }}>
                            <span style={{ 
                              padding: "0.25rem 0.5rem", 
                              borderRadius: "4px", 
                              fontSize: "0.8rem",
                              backgroundColor: "#e2e3e5",
                              color: "#383d41"
                            }}>
                              {getAccionText(item.accion)}
                            </span>
                          </td>
                          <td style={{ padding: "0.5rem", fontWeight: "500" }}>{item.admin_que_realizo_cambio}</td>
                          <td style={{ padding: "0.5rem" }}>
                            <div>
                              {item.descripcion}
                              {item.campo && (
                                <div style={{ fontSize: "0.8rem", color: "#666", marginTop: "0.25rem" }}>
                                  <strong>Campo:</strong> {item.campo}
                                  {item.valor_anterior && <span> | <strong>Anterior:</strong> {item.valor_anterior}</span>}
                                  {item.valor_nuevo && <span> | <strong>Nuevo:</strong> {item.valor_nuevo}</span>}
                                </div>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div style={{ position: "fixed", bottom: 24, right: 24, zIndex: 2000 }}>
          <Toast 
            message={toast.message} 
            type={toast.type} 
            onClose={() => setToast(null)}
          />
        </div>
      )}
    </>
  );
};

export default UserManagementModal; 
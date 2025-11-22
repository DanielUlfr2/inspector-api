import React, { useState } from "react";
import { useUser } from "../context/UserContext";
import "../styles/login.css";
import { useNavigate } from "react-router-dom";
import { FaUser, FaLock } from "react-icons/fa";
import { login as authLogin } from "../services/authService";
import PosterModal from "../components/PosterModal";

const isDemoMode =
  import.meta.env.VITE_DEMO_MODE === 'true' ||
  import.meta.env.MODE === 'demo';

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [showPoster, setShowPoster] = useState(false);
  const { setUser } = useUser();
  const navigate = useNavigate();

  // Verificar si el usuario ya vio el poster
  const hasSeenPoster = (): boolean => {
    return localStorage.getItem('inspector_poster_seen') === 'true';
  };

  // Marcar que el usuario ya vio el poster
  const markPosterAsSeen = (): void => {
    localStorage.setItem('inspector_poster_seen', 'true');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await authLogin({ username, password });
      
      // Usar la información del usuario que viene en la respuesta
      setUser({
        token: data.access_token,
        id: data.user.id,
        nombre: data.user.username,
        rol: data.user.rol,
        foto: data.user.foto_perfil
      });
      
      // Verificar si el usuario ya vio el poster
      if (!hasSeenPoster()) {
        // Mostrar el poster solo si no lo ha visto antes
        setShowPoster(true);
      } else {
        // Si ya lo vio, ir directamente al dashboard
        navigate("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Usuario o contraseña incorrectos");
    }
  };

  const handleClosePoster = () => {
    setShowPoster(false);
    // Marcar que el usuario ya vio el poster
    markPosterAsSeen();
    // Redirigir al dashboard después de cerrar el poster
    navigate("/dashboard");
  };

  return (
    <div className="login-bg-tigo-soft">
      <div className="login-card">
        <img src={`${import.meta.env.BASE_URL}logo-inspector.png`} alt="Inspector" className="login-logo-tigo" />
        <h2 className="login-title-tigo">Iniciar Sesión</h2>
        {isDemoMode && (
          <div style={{
            backgroundColor: '#e0f2fe',
            border: '1px solid #0284c7',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '20px',
            fontSize: '14px',
            color: '#0c4a6e'
          }}>
            <div style={{ fontWeight: 'bold', marginBottom: '8px' }}>🎭 Modo Demo</div>
            <div>Usuario: <strong>demo</strong></div>
            <div>Contraseña: <strong>demo123</strong></div>
          </div>
        )}
        <form className="login-form-tigo" onSubmit={handleSubmit}>
          <div className="input-group-tigo">
            <span className="input-icon-tigo"><FaUser /></span>
            <input
              type="text"
              placeholder="Usuario"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="input-group-tigo">
            <span className="input-icon-tigo"><FaLock /></span>
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="login-error-tigo">{error}</div>}
          <button type="submit" className="login-btn-tigo">Acceder</button>
        </form>
      </div>
      <PosterModal
        isOpen={showPoster}
        onClose={handleClosePoster}
        posterUrl={`${import.meta.env.BASE_URL}poster.jpg`}
      />
    </div>
  );
}
import React, { useState } from "react";
import { useUser } from "../context/UserContext";
import "../styles/login.css";
import { useNavigate } from "react-router-dom";
import { FaUser, FaLock } from "react-icons/fa";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { setUser } = useUser();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) throw new Error("Credenciales inválidas");

      const data = await response.json();
      
      // Debug: verificar la respuesta del backend
      console.log('Respuesta del login:', data);
      console.log('ID del usuario:', data.user.id);
      console.log('Foto del usuario:', data.user.foto);
      console.log('Todos los campos del usuario:', data.user);
      
      // Guardar token en localStorage para persistencia
      localStorage.setItem("token", data.access_token);
      
      // Usar la información del usuario que viene en la respuesta
      setUser({
        token: data.access_token,
        id: data.user.id,
        nombre: data.user.username,
        rol: data.user.rol,
        foto: data.user.foto
      });
      
      // Redirigir al dashboard usando React Router
      navigate("/dashboard");
    } catch (err) {
      setError("Usuario o contraseña incorrectos");
    }
  };

  return (
    <div className="login-bg-tigo-soft">
      <div className="login-card">
        <img src="/logo-inspector.png" alt="Inspector" className="login-logo-tigo" />
        <h2 className="login-title-tigo">Iniciar Sesión</h2>
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
    </div>
  );
}
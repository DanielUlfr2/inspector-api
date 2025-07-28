
import React, { createContext, useContext, useState, ReactNode, useEffect } from "react";

type UserRole = "admin" | "user" | null;

interface UserContextType {
  token: string | null;
  id: number | null;
  nombre: string | null;
  rol: UserRole;
  foto: string | null;
  setUser: (userData: {
    token: string;
    id: number;
    nombre: string;
    rol: UserRole;
    foto?: string;
  }) => void;
  updateUser: (userData: {
    id?: number;
    nombre?: string;
    rol?: UserRole;
    foto?: string;
  }) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);
  const [id, setId] = useState<number | null>(null);
  const [nombre, setNombre] = useState<string | null>(null);
  const [rol, setRol] = useState<UserRole>(null);
  const [foto, setFoto] = useState<string | null>(null);

  // Inicializar token desde localStorage al cargar
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  const setUser = ({
    token,
    id,
    nombre,
    rol,
    foto,
  }: {
    token: string;
    id: number;
    nombre: string;
    rol: UserRole;
    foto?: string;
  }) => {
    console.log('Guardando usuario en contexto:', { token, id, nombre, rol, foto });
    setToken(token);
    setId(id);
    setNombre(nombre);
    setRol(rol);
    if (foto) setFoto(foto);
  };

  const updateUser = (userData: {
    id?: number;
    nombre?: string;
    rol?: UserRole;
    foto?: string;
  }) => {
    if (userData.id) setId(userData.id);
    if (userData.nombre) setNombre(userData.nombre);
    if (userData.rol) setRol(userData.rol);
    if (userData.foto) setFoto(userData.foto);
  };

  const logout = () => {
    setToken(null);
    setId(null);
    setNombre(null);
    setRol(null);
    setFoto(null);
    localStorage.removeItem("token");
  };

  return (
    <UserContext.Provider value={{ token, id, nombre, rol, foto, setUser, updateUser, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser debe usarse dentro de un UserProvider");
  }
  return context;
};

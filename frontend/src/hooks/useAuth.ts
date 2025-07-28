import { useState, useEffect, useCallback } from 'react';
import { getToken, isAuthenticated, logout, isTokenExpiringSoon, refreshToken } from '../services/authService';
import { User } from '../types/Auth';

interface UseAuthReturn {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  logout: () => void;
  checkAuthStatus: () => void;
}

export function useAuth(): UseAuthReturn {
  const [isAuth, setIsAuth] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Función para verificar el estado de autenticación
  const checkAuthStatus = useCallback(async () => {
    try {
      setLoading(true);
      
      const hasToken = isAuthenticated();
      setIsAuth(hasToken);

      if (hasToken) {
        // Verificar si el token está próximo a expirar
        if (isTokenExpiringSoon()) {
          console.log('Token próximo a expirar, intentando renovar...');
          const refreshed = await refreshToken();
          
          if (!refreshed) {
            console.log('No se pudo renovar el token, cerrando sesión...');
            handleLogout();
            return;
          }
        }

        // Obtener información del usuario si está disponible
        const userData = localStorage.getItem('user');
        if (userData) {
          try {
            const parsedUser = JSON.parse(userData);
            setUser(parsedUser);
          } catch (error) {
            console.error('Error al parsear datos del usuario:', error);
            setUser(null);
          }
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error al verificar estado de autenticación:', error);
      setIsAuth(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Función para cerrar sesión
  const handleLogout = useCallback(() => {
    logout();
    setIsAuth(false);
    setUser(null);
    
    // Redirigir al login si no estamos ya ahí
    if (!window.location.pathname.includes('/')) {
      window.location.href = '/';
    }
  }, []);

  // Verificar estado de autenticación al montar el componente
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Verificar periódicamente si el token está próximo a expirar
  useEffect(() => {
    if (!isAuth) return;

    const interval = setInterval(async () => {
      if (isTokenExpiringSoon()) {
        console.log('Token próximo a expirar, renovando...');
        const refreshed = await refreshToken();
        
        if (!refreshed) {
          console.log('No se pudo renovar el token automáticamente');
          // No cerrar sesión automáticamente aquí, dejar que el usuario continúe
          // hasta que haga una petición que falle
        }
      }
    }, 60000); // Verificar cada minuto

    return () => clearInterval(interval);
  }, [isAuth]);

  return {
    isAuthenticated: isAuth,
    user,
    loading,
    logout: handleLogout,
    checkAuthStatus,
  };
} 
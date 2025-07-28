import React from 'react';
import { useAuth } from '../hooks/useAuth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  fallback = <div>Cargando...</div> 
}) => {
  const { isAuthenticated, loading } = useAuth();

  // Mostrar fallback mientras se verifica la autenticación
  if (loading) {
    return <>{fallback}</>;
  }

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated) {
    window.location.href = '/';
    return null;
  }

  // Si está autenticado, mostrar el contenido protegido
  return <>{children}</>;
};

export default ProtectedRoute; 
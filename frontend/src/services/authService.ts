import { LoginCredentials, LoginResponse, User } from '../types/Auth';

const isDemoMode =
  import.meta.env.VITE_DEMO_MODE === 'true' ||
  import.meta.env.MODE === 'demo';

const DEMO_USER: LoginResponse = {
  access_token: 'demo-token',
  token_type: 'bearer',
  user: {
    id: 0,
    username: 'Demo Admin',
    rol: 'admin',
    foto_perfil: undefined,
  },
};

// Función para obtener el token de autenticación desde localStorage
export function getToken(): string | null {
  return localStorage.getItem('token');
}

// Función para guardar el token en localStorage
export function setToken(token: string): void {
  localStorage.setItem('token', token);
}

// Función para eliminar el token de localStorage
export function removeToken(): void {
  localStorage.removeItem('token');
}

// Función para verificar si el usuario está autenticado
export function isAuthenticated(): boolean {
  if (isDemoMode) {
    return localStorage.getItem('user') !== null;
  }
  const token = getToken();
  return token !== null && token !== '';
}

// Función para hacer login
export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  try {
    if (isDemoMode) {
      const { username, password } = credentials;
      if (username === 'demo' && password === 'demo123') {
        setToken(DEMO_USER.access_token);
        localStorage.setItem('user', JSON.stringify(DEMO_USER.user));
        return DEMO_USER;
      }
      throw new Error('Credenciales incorrectas');
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error en el login');
    }

    const data: LoginResponse = await response.json();
    setToken(data.access_token);
    return data;
  } catch (error) {
    console.error('Error en login:', error);
    throw error;
  }
}

// Función para hacer logout - limpia completamente la sesión
export function logout(): void {
  // Limpiar token
  removeToken();
  
  // Limpiar datos del usuario
  localStorage.removeItem('user');
  
  // Limpiar cualquier otro dato de sesión que pueda existir
  localStorage.removeItem('auth');
  localStorage.removeItem('session');
  
  // Limpiar sessionStorage también
  sessionStorage.clear();
  
  // Limpiar cookies relacionadas con la sesión (si las hay)
  document.cookie.split(";").forEach(function(c) { 
    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/"); 
  });
  
  console.log('Sesión cerrada completamente');
}

// Función para obtener información del usuario actual
export function getCurrentUser(): User | null {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }
  return null;
}

// Función para guardar información del usuario
export function setCurrentUser(user: User): void {
  localStorage.setItem('user', JSON.stringify(user));
}

// Función para verificar si el token está próximo a expirar
export function isTokenExpiringSoon(): boolean {
  const token = getToken();
  if (!token) return false;
  
  try {
    // Decodificar el token JWT (solo la parte del payload)
    const payload = JSON.parse(atob(token.split('.')[1]));
    const expirationTime = payload.exp * 1000; // Convertir a milisegundos
    const currentTime = Date.now();
    const timeUntilExpiration = expirationTime - currentTime;
    
    // Considerar que está próximo a expirar si faltan menos de 5 minutos
    return timeUntilExpiration < 5 * 60 * 1000;
  } catch (error) {
    console.error('Error al verificar expiración del token:', error);
    return false;
  }
}

// Función para renovar el token automáticamente
export async function refreshToken(): Promise<boolean> {
  if (isDemoMode) {
    return false;
  }
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      const data = await response.json();
      setToken(data.access_token);
      return true;
    }
    
    return false;
  } catch (error) {
    console.error('Error al renovar token:', error);
    return false;
  }
} 
import { UserRole } from '../constants/roles';

export interface User {
  id: number;
  username: string;
  rol: UserRole;
  foto_perfil?: string;
}

export interface AuthContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
} 
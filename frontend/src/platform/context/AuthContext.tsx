import { createContext, useReducer, useCallback, useEffect, type ReactNode } from 'react';
import type { User, UserRole, Permission } from '@/types';
import { ROLE_PERMISSIONS } from '@/constants';
import { loginByRole } from '@/services/authService';
import { initializeMockData } from '@/mock';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGIN_FAILURE' }
  | { type: 'LOGOUT' };

interface AuthContextValue extends AuthState {
  login: (role: UserRole) => Promise<void>;
  logout: () => void;
  hasPermission: (permission: Permission) => boolean;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true };
    case 'LOGIN_SUCCESS':
      return { user: action.payload, isAuthenticated: true, isLoading: false };
    case 'LOGIN_FAILURE':
      return { user: null, isAuthenticated: false, isLoading: false };
    case 'LOGOUT':
      return { user: null, isAuthenticated: false, isLoading: false };
    default:
      return state;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isAuthenticated: false,
    isLoading: false,
  });

  useEffect(() => {
    initializeMockData();
  }, []);

  const login = useCallback(async (role: UserRole) => {
    dispatch({ type: 'LOGIN_START' });
    try {
      const user = await loginByRole(role);
      dispatch({ type: 'LOGIN_SUCCESS', payload: user });
    } catch {
      dispatch({ type: 'LOGIN_FAILURE' });
    }
  }, []);

  const logout = useCallback(() => {
    dispatch({ type: 'LOGOUT' });
  }, []);

  const hasPermission = useCallback(
    (permission: Permission): boolean => {
      if (!state.user) return false;
      const permissions = ROLE_PERMISSIONS[state.user.role];
      return permissions.includes(permission);
    },
    [state.user]
  );

  return (
    <AuthContext.Provider value={{ ...state, login, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
}

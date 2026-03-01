import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as authApi from '../api/auth.js';
import { setStoredTokens, clearStoredTokens, getStoredTokens } from '../api/base.js';
import { ROLES } from '../config/index.js';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const tokens = getStoredTokens();
    if (!tokens?.access && !tokens?.access_token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await authApi.getMe();
      setUser(me);
    } catch {
      clearStoredTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(async (usernameOrEmail, password) => {
    await authApi.login(usernameOrEmail, password);
    const me = await authApi.getMe();
    setUser(me);
    return me;
  }, []);

  const registerUser = useCallback(async (payload) => {
    await authApi.register(payload);
    await authApi.login(payload.email, payload.password);
    const me = await authApi.getMe();
    setUser(me);
    return me;
  }, []);

  const logout = useCallback(() => {
    clearStoredTokens();
    setUser(null);
  }, []);

  const isOrganizerOrAdmin = user && (user.role === ROLES.organizer || user.role === ROLES.admin);

  const value = {
    user,
    loading,
    login,
    registerUser,
    logout,
    isOrganizerOrAdmin,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

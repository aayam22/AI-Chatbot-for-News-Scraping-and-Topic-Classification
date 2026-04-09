import { useState, useEffect, useCallback } from 'react';
import { STORAGE_KEYS } from '../constants/config';

/**
 * Custom hook for authentication token management
 */
export const useAuth = () => {
  const [token, setTokenState] = useState(() => 
    localStorage.getItem(STORAGE_KEYS.TOKEN) || null
  );

  const setToken = useCallback((newToken) => {
    if (newToken) {
      localStorage.setItem(STORAGE_KEYS.TOKEN, newToken);
    } else {
      localStorage.removeItem(STORAGE_KEYS.TOKEN);
    }
    setTokenState(newToken);
  }, []);

  const logout = useCallback(() => {
    setToken(null);
  }, [setToken]);

  const isAuthenticated = !!token;

  return { token, setToken, logout, isAuthenticated };
};

export default useAuth;

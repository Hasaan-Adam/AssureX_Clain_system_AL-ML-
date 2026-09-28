import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authAPI from '../api/authAPI';
import { ROLES } from '../utils/constants';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('assurex_user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch (e) {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('assurex_token') || null);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  const checkAuth = useCallback(async () => {
    const storedToken = localStorage.getItem('assurex_token');
    if (!storedToken) {
      setUser(null);
      setToken(null);
      setLoading(false);
      return;
    }

    try {
      const response = await authAPI.getCurrentUser();
      const userData = response.data || response.user || response;
      setUser(userData);
      localStorage.setItem('assurex_user', JSON.stringify(userData));
    } catch (err) {
      console.warn('Session verification failed, logging out.');
      setUser(null);
      setToken(null);
      localStorage.removeItem('assurex_token');
      localStorage.removeItem('assurex_user');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();

    const handleUnauthorized = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, [checkAuth]);

  const login = async (credentials) => {
    setAuthError(null);
    try {
      const res = await authAPI.login(credentials);
      const resData = res.data || res;
      const accessToken = resData.access_token || resData.token;
      const userData = resData.user || {
        id: resData.id,
        email: resData.email,
        full_name: resData.full_name,
        role: resData.role || ROLES.CUSTOMER,
      };

      if (accessToken) {
        localStorage.setItem('assurex_token', accessToken);
        setToken(accessToken);
      }
      if (userData) {
        localStorage.setItem('assurex_user', JSON.stringify(userData));
        setUser(userData);
      }
      return { success: true, user: userData };
    } catch (err) {
      const msg = err.message || 'Login failed. Please verify credentials.';
      setAuthError(msg);
      return { success: false, error: msg };
    }
  };

  const register = async (userData) => {
    setAuthError(null);
    try {
      const res = await authAPI.register(userData);
      const resData = res.data || res;
      const accessToken = resData.access_token || resData.token;
      const registeredUser = resData.user || {
        id: resData.id,
        email: resData.email,
        full_name: resData.full_name,
        role: resData.role || ROLES.CUSTOMER,
      };

      if (accessToken) {
        localStorage.setItem('assurex_token', accessToken);
        setToken(accessToken);
      }
      if (registeredUser) {
        localStorage.setItem('assurex_user', JSON.stringify(registeredUser));
        setUser(registeredUser);
      }
      return { success: true, user: registeredUser };
    } catch (err) {
      const msg = err.message || 'Registration failed.';
      setAuthError(msg);
      return { success: false, error: msg };
    }
  };

  const logout = async () => {
    await authAPI.logout();
    setUser(null);
    setToken(null);
    setAuthError(null);
  };

  const updateUser = (updatedFields) => {
    setUser((prev) => {
      const updated = { ...prev, ...updatedFields };
      localStorage.setItem('assurex_user', JSON.stringify(updated));
      return updated;
    });
  };

  const role = (user?.role || '').toLowerCase();
  const isAdmin = role === ROLES.ADMIN;
  const isReviewer = role === ROLES.REVIEWER;
  const isStaff = role === ROLES.STAFF || role === 'service_staff' || isReviewer || isAdmin;
  const isCustomer = role === ROLES.CUSTOMER || (!isAdmin && !isReviewer && !isStaff);
  const isAuthenticated = !!token && !!user;

  const value = {
    user,
    token,
    loading,
    authError,
    isAuthenticated,
    isAdmin,
    isReviewer,
    isStaff,
    isCustomer,
    login,
    register,
    logout,
    updateUser,
    refreshUser: checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
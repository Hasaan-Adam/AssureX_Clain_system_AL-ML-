import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import notificationAPI from '../api/notificationAPI';

const NotificationContext = createContext(null);

export const NotificationProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);
  const [warrantyAlerts, setWarrantyAlerts] = useState([]);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const unreadCount = notifications.filter(n => !n.is_read).length;

  const fetchNotifications = useCallback(async () => {
    try {
      const response = await notificationAPI.getNotifications();
      const data = response.data;
      if (Array.isArray(data)) {
        setNotifications(data);
      } else if (data && data.notifications) {
        setNotifications(data.notifications);
      } else {
        setNotifications([]);
      }
    } catch (error) {
      console.error('Failed to fetch notifications', error);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('assurex_token');
    if (token) {
      fetchNotifications();
      const intervalId = setInterval(() => {
        fetchNotifications();
      }, 10000); // Check every 10 seconds for real-time notifications
      return () => clearInterval(intervalId);
    }
  }, [fetchNotifications]);

  const handleMarkRead = async (id) => {
    try {
      await notificationAPI.markAsRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (error) {
      console.error('Failed to mark read', error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (error) {
      console.error('Failed to mark all read', error);
    }
  };

  const addToast = useCallback((message, type = 'info', duration = 5000) => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2, 6);
    const newToast = { id, message, type, duration };

    setToasts((prev) => [...prev, newToast]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }

    return id;
  }, []);

  const toastSuccess = useCallback((msg, duration) => addToast(msg, 'success', duration), [addToast]);
  const toastError = useCallback((msg, duration) => addToast(msg, 'error', duration || 6000), [addToast]);
  const toastWarning = useCallback((msg, duration) => addToast(msg, 'warning', duration), [addToast]);
  const toastInfo = useCallback((msg, duration) => addToast(msg, 'info', duration), [addToast]);

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showWarrantyAlerts = useCallback((alertsList) => {
    if (alertsList && alertsList.length > 0) {
      setWarrantyAlerts(alertsList);
      setIsAlertModalOpen(true);
    }
  }, []);

  const closeWarrantyAlerts = useCallback(() => {
    setIsAlertModalOpen(false);
  }, []);

  const value = {
    toasts,
    addToast,
    removeToast,
    toastSuccess,
    toastError,
    toastWarning,
    toastInfo,
    warrantyAlerts,
    showWarrantyAlerts,
    isAlertModalOpen,
    closeWarrantyAlerts,
    notifications,
    unreadCount,
    fetchNotifications,
    handleMarkRead,
    handleMarkAllRead,
  };

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

export default NotificationContext;
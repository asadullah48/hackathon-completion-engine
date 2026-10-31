'use client';

import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Define types
type NotificationType = 'info' | 'success' | 'warning' | 'error';

interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  userId?: string;
  teamId?: string;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  removeNotification: (id: string) => void;
}

// Create context
const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

// Reducer for state management
type NotificationAction =
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'MARK_AS_READ'; payload: string }
  | { type: 'MARK_ALL_AS_READ' }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'CLEAR_ALL' };

const notificationReducer = (state: Notification[], action: NotificationAction): Notification[] => {
  switch (action.type) {
    case 'ADD_NOTIFICATION':
      return [action.payload, ...state];
    case 'MARK_AS_READ':
      return state.map(notification =>
        notification.id === action.payload ? { ...notification, read: true } : notification
      );
    case 'MARK_ALL_AS_READ':
      return state.map(notification => ({ ...notification, read: true }));
    case 'REMOVE_NOTIFICATION':
      return state.filter(notification => notification.id !== action.payload);
    case 'CLEAR_ALL':
      return [];
    default:
      return state;
  }
};

// Provider component
interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, dispatch] = useReducer(notificationReducer, []);

  // Initialize from localStorage
  useEffect(() => {
    const savedNotifications = localStorage.getItem('notifications');
    if (savedNotifications) {
      try {
        const parsed = JSON.parse(savedNotifications);
        // Convert string dates back to Date objects
        const notificationsWithDates = parsed.map((n: any) => ({
          ...n,
          timestamp: new Date(n.timestamp)
        }));
        dispatch({ type: 'CLEAR_ALL' });
        notificationsWithDates.forEach((n: Notification) => {
          dispatch({ type: 'ADD_NOTIFICATION', payload: n });
        });
      } catch (e) {
        console.error('Failed to parse notifications from localStorage', e);
      }
    }
  }, []);

  // Save to localStorage whenever notifications change
  useEffect(() => {
    const serialized = notifications.map(n => ({
      ...n,
      timestamp: n.timestamp.toISOString()
    }));
    localStorage.setItem('notifications', JSON.stringify(serialized));
  }, [notifications]);

  // Calculate unread count
  const unreadCount = notifications.filter(n => !n.read).length;

  // Add a new notification
  const addNotification = (notificationData: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notificationData,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      read: false
    };

    dispatch({ type: 'ADD_NOTIFICATION', payload: newNotification });

    // Show toast notification based on type
    switch (notificationData.type) {
      case 'success':
        toast.success(`${notificationData.title}: ${notificationData.message}`);
        break;
      case 'error':
        toast.error(`${notificationData.title}: ${notificationData.message}`);
        break;
      case 'warning':
        toast.warn(`${notificationData.title}: ${notificationData.message}`);
        break;
      case 'info':
      default:
        toast.info(`${notificationData.title}: ${notificationData.message}`);
        break;
    }
  };

  // Mark a notification as read
  const markAsRead = (id: string) => {
    dispatch({ type: 'MARK_AS_READ', payload: id });
  };

  // Mark all notifications as read
  const markAllAsRead = () => {
    dispatch({ type: 'MARK_ALL_AS_READ' });
  };

  // Remove a notification
  const removeNotification = (id: string) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: id });
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        unreadCount,
        addNotification,
        markAsRead,
        markAllAsRead,
        removeNotification
      }}
    >
      {children}
      <ToastContainer position="bottom-right" autoClose={5000} hideProgressBar={false} newestOnTop closeOnClick rtl={false} pauseOnFocusLoss draggable pauseOnHover theme="light" />
    </NotificationContext.Provider>
  );
};

// Custom hook to use the notification context
export const useNotifications = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
'use client';

import { Bell, Mail, CheckCircle } from 'lucide-react';
import { useNotifications } from '@/components/NotificationProvider';
import { useState } from 'react';

export default function NotificationBadge() {
  const { notifications, unreadCount, markAllAsRead } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const handleMarkAllAsRead = () => {
    markAllAsRead();
    setIsOpen(false);
  };

  // Get the 5 most recent notifications
  const recentNotifications = notifications.slice(0, 5);

  return (
    <div className="relative">
      <button
        onClick={toggleDropdown}
        className="relative p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-200 transition-colors"
        title="Notifications"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute top-0 right-0 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          <div className="p-4 border-b border-gray-200 flex justify-between items-center">
            <h3 className="font-medium text-gray-900">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllAsRead}
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <CheckCircle className="w-4 h-4" />
                Mark all as read
              </button>
            )}
          </div>
          
          <div className="max-h-96 overflow-y-auto">
            {recentNotifications.length > 0 ? (
              <ul>
                {recentNotifications.map((notification) => (
                  <li 
                    key={notification.id} 
                    className={`p-4 border-b border-gray-100 ${!notification.read ? 'bg-blue-50' : 'bg-white'}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`flex-shrink-0 w-2 h-2 mt-1.5 rounded-full ${!notification.read ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{notification.message}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(notification.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="p-8 text-center">
                <Mail className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">No notifications</p>
              </div>
            )}
          </div>
          
          {notifications.length > 5 && (
            <div className="p-3 text-center text-sm text-gray-500 border-t border-gray-200">
              Showing 5 of {notifications.length} notifications
            </div>
          )}
        </div>
      )}
    </div>
  );
}
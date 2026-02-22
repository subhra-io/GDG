'use client';

import { useState, useEffect } from 'react';
import { Bell, Check, AlertCircle, Info, CheckCircle, Filter } from 'lucide-react';
import Link from 'next/link';

interface Notification {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  channel: string;
  status: string;
  is_read: boolean;
  created_at: string;
  violation_id?: string;
  metadata?: any;
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread'>('all');
  const [stats, setStats] = useState<any>(null);
  
  // Default user ID (in production, get from auth context)
  const userId = "e90cf88e-cb4b-4fe3-8098-6759d500b260";

  useEffect(() => {
    fetchNotifications();
    fetchStatistics();
  }, [filter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const url = filter === 'unread'
        ? `http://localhost:8000/api/v1/notifications/user/${userId}?unread_only=true&limit=100`
        : `http://localhost:8000/api/v1/notifications/user/${userId}?limit=100`;
      
      const response = await fetch(url);
      const data = await response.json();
      setNotifications(data.notifications || []);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/notifications/statistics?user_id=${userId}`
      );
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(
        `http://localhost:8000/api/v1/notifications/${notificationId}/read`,
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId })
        }
      );
      
      fetchNotifications();
      fetchStatistics();
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await fetch(
        'http://localhost:8000/api/v1/notifications/mark-all-read',
        {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId })
        }
      );
      
      fetchNotifications();
      fetchStatistics();
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const getNotificationIcon = (type: string, metadata: any) => {
    const severity = metadata?.severity?.toLowerCase();
    
    if (type === 'violation') {
      if (severity === 'critical') return <AlertCircle className="w-6 h-6 text-red-600" />;
      if (severity === 'high') return <AlertCircle className="w-6 h-6 text-orange-600" />;
      if (severity === 'medium') return <AlertCircle className="w-6 h-6 text-yellow-600" />;
      return <AlertCircle className="w-6 h-6 text-blue-600" />;
    }
    
    if (type === 'review') {
      return <CheckCircle className="w-6 h-6 text-green-600" />;
    }
    
    return <Info className="w-6 h-6 text-gray-600" />;
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Bell className="w-8 h-8" />
            Notifications
          </h1>
          <p className="mt-2 text-gray-600">
            View and manage your notification history
          </p>
        </div>

        {/* Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600">Total</div>
              <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600">Unread</div>
              <div className="text-2xl font-bold text-blue-600">{stats.unread}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600">Read</div>
              <div className="text-2xl font-bold text-green-600">{stats.read}</div>
            </div>
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-sm text-gray-600">Violations</div>
              <div className="text-2xl font-bold text-red-600">
                {stats.by_type?.violation || 0}
              </div>
            </div>
          </div>
        )}

        {/* Filters and Actions */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Filter className="w-5 h-5 text-gray-400" />
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg ${
                  filter === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilter('unread')}
                className={`px-4 py-2 rounded-lg ${
                  filter === 'unread'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Unread
              </button>
            </div>
            
            {stats && stats.unread > 0 && (
              <button
                onClick={markAllAsRead}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Mark All as Read
              </button>
            )}
          </div>
        </div>

        {/* Notifications List */}
        <div className="bg-white rounded-lg shadow">
          {loading ? (
            <div className="p-12 text-center text-gray-500">
              Loading notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-12 text-center text-gray-500">
              <Bell className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">No notifications found</p>
              <p className="text-sm mt-2">
                {filter === 'unread' ? 'All caught up!' : 'Notifications will appear here'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`p-6 hover:bg-gray-50 transition-colors ${
                    !notification.is_read ? 'bg-blue-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.notification_type, notification.metadata)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {notification.title}
                          </h3>
                          <p className="mt-1 text-gray-600">
                            {notification.message}
                          </p>
                          
                          <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                            <span>{formatTime(notification.created_at)}</span>
                            <span className="px-2 py-1 bg-gray-100 rounded">
                              {notification.channel}
                            </span>
                            <span className={`px-2 py-1 rounded ${
                              notification.status === 'sent'
                                ? 'bg-green-100 text-green-800'
                                : notification.status === 'failed'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {notification.status}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-2">
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification.id)}
                              className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm flex items-center gap-1"
                            >
                              <Check className="w-4 h-4" />
                              Mark Read
                            </button>
                          )}
                          
                          {notification.violation_id && (
                            <Link
                              href={`/violations/${notification.violation_id}`}
                              className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
                            >
                              View Details
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Link to Alert Rules */}
        <div className="mt-6 text-center">
          <Link
            href="/settings/alerts"
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Configure Alert Rules →
          </Link>
        </div>
      </div>
    </div>
  );
}

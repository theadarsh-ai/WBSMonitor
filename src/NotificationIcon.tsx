import { useState, useEffect } from 'react'
import './NotificationIcon.css'

const API_URL = ''

interface Notification {
  id: string
  type: string
  severity: 'info' | 'warning' | 'error'
  task_name: string
  action: string
  message: string
  timestamp: string
  read: boolean
}

interface NotificationResponse {
  notifications: Notification[]
  unread_count: number
  total_count: number
}

function NotificationIcon() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${API_URL}/api/notifications`)
      if (!response.ok) throw new Error('Failed to fetch notifications')
      const data: NotificationResponse = await response.json()
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch (err) {
      console.error('Error fetching notifications:', err)
    }
  }

  const markAsRead = async (notificationId: string) => {
    try {
      await fetch(`${API_URL}/api/notifications/${notificationId}/read`, {
        method: 'POST',
      })
      await fetchNotifications()
    } catch (err) {
      console.error('Error marking notification as read:', err)
    }
  }

  const clearAllNotifications = async () => {
    setLoading(true)
    try {
      await fetch(`${API_URL}/api/notifications/clear`, {
        method: 'POST',
      })
      await fetchNotifications()
      setIsOpen(false)
    } catch (err) {
      console.error('Error clearing notifications:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleDropdown = () => {
    setIsOpen(!isOpen)
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'warning':
        return '⚠️'
      case 'error':
        return '🚨'
      case 'info':
      default:
        return 'ℹ️'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  useEffect(() => {
    fetchNotifications()
    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="notification-container">
      <button className="notification-bell" onClick={toggleDropdown}>
        <span className="bell-icon">🔔</span>
        {unreadCount > 0 && (
          <span className="notification-badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
        )}
      </button>

      {isOpen && (
        <>
          <div className="notification-overlay" onClick={() => setIsOpen(false)} />
          <div className="notification-dropdown">
            <div className="notification-header">
              <h3>Self-Healing Notifications</h3>
              {notifications.length > 0 && (
                <button
                  onClick={clearAllNotifications}
                  className="clear-all-btn"
                  disabled={loading}
                >
                  {loading ? 'Clearing...' : 'Clear All'}
                </button>
              )}
            </div>

            <div className="notification-list">
              {notifications.length === 0 ? (
                <div className="no-notifications">
                  <p>✨ No notifications</p>
                  <p className="no-notifications-subtitle">
                    All systems running smoothly
                  </p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`notification-item ${!notification.read ? 'unread' : ''}`}
                    onClick={() => !notification.read && markAsRead(notification.id)}
                  >
                    <div className="notification-icon">
                      {getSeverityIcon(notification.severity)}
                    </div>
                    <div className="notification-content">
                      <div className="notification-message">{notification.message}</div>
                      <div className="notification-meta">
                        <span className="notification-time">
                          {formatTimestamp(notification.timestamp)}
                        </span>
                        <span className="notification-task">
                          {notification.task_name}
                        </span>
                      </div>
                    </div>
                    {!notification.read && <div className="unread-dot"></div>}
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default NotificationIcon

import React, { useState, useEffect } from 'react';
import './Notification.css';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

interface NotificationProps {
  message: string;
  type: NotificationType;
  duration?: number;
  onClose?: () => void;
  show?: boolean;
}

const Notification: React.FC<NotificationProps> = ({
  message,
  type = 'info',
  duration = 5000,
  onClose,
  show = true
}) => {
  const [isVisible, setIsVisible] = useState(show);

  useEffect(() => {
    setIsVisible(show);
  }, [show]);

  useEffect(() => {
    if (isVisible && duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✅';
      case 'error':
        return '❌';
      case 'warning':
        return '⚠️';
      case 'info':
        return 'ℹ️';
      default:
        return 'ℹ️';
    }
  };

  return (
    <div className={`notification notification--${type}`}>
      <div className="notification__content">
        <div className="notification__icon">
          {getIcon()}
        </div>
        <div className="notification__message">
          {message}
        </div>
        <button 
          className="notification__close"
          onClick={handleClose}
          aria-label="Cerrar notificación"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default Notification; 
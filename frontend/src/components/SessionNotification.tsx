import React, { useState, useEffect } from 'react';
import './SessionNotification.css';

interface SessionNotificationProps {
  message: string;
  type: 'error' | 'warning' | 'info';
  duration?: number;
  onClose?: () => void;
}

const SessionNotification: React.FC<SessionNotificationProps> = ({
  message,
  type = 'info',
  duration = 5000,
  onClose
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  if (!isVisible) return null;

  return (
    <div className={`session-notification session-notification--${type}`}>
      <div className="session-notification__content">
        <div className="session-notification__icon">
          {type === 'error' && '⚠️'}
          {type === 'warning' && '⚠️'}
          {type === 'info' && 'ℹ️'}
        </div>
        <div className="session-notification__message">
          {message}
        </div>
        <button 
          className="session-notification__close"
          onClick={handleClose}
          aria-label="Cerrar notificación"
        >
          ✕
        </button>
      </div>
    </div>
  );
};

export default SessionNotification; 
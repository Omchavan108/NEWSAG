import { useState, useEffect } from 'react';

interface Notification {
  message: string;
  type: 'error' | 'success';
}

const AUTO_DISMISS_TIMEOUT = 5000;

export const useNotification = () => {
  const [notification, setNotification] = useState<Notification | null>(null);

  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), AUTO_DISMISS_TIMEOUT);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const showNotification = (message: string, type: 'error' | 'success' = 'error') => {
    setNotification({ message, type });
  };

  const hideNotification = () => setNotification(null);

  return { notification, showNotification, hideNotification };
};

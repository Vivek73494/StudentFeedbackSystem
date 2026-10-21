import React, { useEffect } from 'react';

export default function Alert({ type = 'info', message, onClose, duration = 4000 }) {
  useEffect(() => {
    if (!message || !duration) return;
    const timer = setTimeout(() => {
      if (onClose) onClose();
    }, duration);
    return () => clearTimeout(timer);
  }, [message, duration, onClose]);

  if (!message) return null;

  return (
    <div className={`flash-alert ${type}`}>
      <span>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '1.2rem',
            cursor: 'pointer',
            marginLeft: '12px',
            lineHeight: 1,
            color: 'inherit',
          }}
          aria-label="Close"
        >
          &times;
        </button>
      )}
    </div>
  );
}

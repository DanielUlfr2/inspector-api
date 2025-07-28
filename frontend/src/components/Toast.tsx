import React, { useEffect } from "react";

export interface ToastProps {
  message: string;
  type?: "success" | "error" | "info";
  onClose: () => void;
  duration?: number;
}

const Toast: React.FC<ToastProps> = ({ message, type = "info", onClose, duration = 3000 }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [onClose, duration]);

  return (
    <div
      style={{
        minWidth: 220,
        maxWidth: 340,
        background: type === "success" ? "#4caf50" : type === "error" ? "#f44336" : "#333",
        color: "#fff",
        padding: "14px 24px",
        borderRadius: 8,
        boxShadow: "0 2px 12px rgba(0,0,0,0.18)",
        marginBottom: 12,
        fontSize: 16,
        display: "flex",
        alignItems: "center",
        gap: 12,
        zIndex: 9999,
        cursor: "pointer"
      }}
      onClick={onClose}
      role="alert"
      aria-live="assertive"
    >
      {type === "success" && <span style={{ fontWeight: "bold" }}>✔</span>}
      {type === "error" && <span style={{ fontWeight: "bold" }}>✖</span>}
      {type === "info" && <span style={{ fontWeight: "bold" }}>ℹ️</span>}
      <span>{message}</span>
    </div>
  );
};

export default Toast; 
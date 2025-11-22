import React, { useEffect } from 'react';
import { FiX } from 'react-icons/fi';
import './PosterModal.css';

interface PosterModalProps {
  isOpen: boolean;
  onClose: () => void;
  posterUrl: string;
}

const PosterModal: React.FC<PosterModalProps> = ({
  isOpen,
  onClose,
  posterUrl
}) => {
  useEffect(() => {
    if (isOpen) {
      // Prevenir scroll del body cuando el modal está abierto
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="poster-modal-overlay"
      onClick={handleOverlayClick}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-label="Poster promocional"
    >
      <div className="poster-modal-content" onClick={(e) => e.stopPropagation()}>
        <button
          className="poster-modal-close"
          onClick={onClose}
          aria-label="Cerrar poster"
          title="Cerrar"
        >
          <FiX size={24} />
        </button>
        <div className="poster-modal-image-container">
          <img
            src={posterUrl}
            alt="Poster promocional Inspector"
            className="poster-modal-image"
          />
        </div>
      </div>
    </div>
  );
};

export default PosterModal;


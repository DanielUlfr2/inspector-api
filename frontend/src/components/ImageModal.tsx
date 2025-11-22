import React from 'react';
import './ImageModal.css';

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  description: string;
  imageAlt?: string;
}

const ImageModal: React.FC<ImageModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  description,
  imageAlt = 'Imagen'
}) => {
  if (!isOpen) return null;

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

  return (
    <div
      className="image-modal-overlay"
      onClick={handleOverlayClick}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="image-modal-description"
    >
      <div className="image-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="image-modal-header">
          <h2 className="image-modal-title">Imagen</h2>
          <button
            className="image-modal-close"
            onClick={onClose}
            aria-label="Cerrar modal"
          >
            ×
          </button>
        </div>
        <div className="image-modal-body">
          <div className="image-modal-image-container">
            <img
              src={imageUrl}
              alt={imageAlt}
              className="image-modal-image"
            />
          </div>
          <div className="image-modal-description" id="image-modal-description">
            {description}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageModal;


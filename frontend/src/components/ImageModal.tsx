import React, { useEffect } from 'react';
import { FiChevronLeft, FiChevronRight, FiX } from 'react-icons/fi';
import './ImageModal.css';

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  description: string;
  imageAlt?: string;
  currentIndex?: number;
  totalImages?: number;
  onPrevious?: () => void;
  onNext?: () => void;
}

const ImageModal: React.FC<ImageModalProps> = ({
  isOpen,
  onClose,
  imageUrl,
  description,
  imageAlt = 'Imagen',
  currentIndex,
  totalImages,
  onPrevious,
  onNext
}) => {
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowLeft' && onPrevious) {
        onPrevious();
      } else if (e.key === 'ArrowRight' && onNext) {
        onNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, onPrevious, onNext]);

  if (!isOpen) return null;

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const canGoPrevious = currentIndex !== undefined && currentIndex > 0;
  const canGoNext = currentIndex !== undefined && totalImages !== undefined && currentIndex < totalImages - 1;

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
          <h2 className="image-modal-title">
            {currentIndex !== undefined && totalImages !== undefined
              ? `Imagen ${currentIndex + 1} de ${totalImages}`
              : 'Imagen'}
          </h2>
          <button
            className="image-modal-close"
            onClick={onClose}
            aria-label="Cerrar modal"
          >
            <FiX size={24} />
          </button>
        </div>
        <div className="image-modal-body">
          <div className="image-modal-image-container">
            {canGoPrevious && onPrevious && (
              <button
                className="image-modal-nav image-modal-nav-prev"
                onClick={onPrevious}
                aria-label="Imagen anterior"
                title="Imagen anterior (←)"
              >
                <FiChevronLeft size={32} />
              </button>
            )}
            <img
              src={imageUrl}
              alt={imageAlt}
              className="image-modal-image"
            />
            {canGoNext && onNext && (
              <button
                className="image-modal-nav image-modal-nav-next"
                onClick={onNext}
                aria-label="Imagen siguiente"
                title="Imagen siguiente (→)"
              >
                <FiChevronRight size={32} />
              </button>
            )}
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


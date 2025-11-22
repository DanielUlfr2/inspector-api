import React, { useState } from "react";
import "../styles/dashboard.css";
import Sidebar from "../components/Sidebar";
import ImageModal from "../components/ImageModal";
import { ImageItem } from "../types/Image";
import "./DashboardImages.css";

const DashboardImages = () => {
  const [selectedImageIndex, setSelectedImageIndex] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Array de imágenes - aquí se agregarán las imágenes con sus descripciones
  const images: ImageItem[] = [
    {
      id: '1',
      url: `${import.meta.env.BASE_URL}images/raspberry-pi-4.jpg`,
      description: 'La Raspberry Pi 4 es un microcomputador compacto y de alto rendimiento que sirve como hardware principal para las sondas Inspector. Sobre este dispositivo se instala el software sincronizado con OpenBalena, permitiendo gestionar, actualizar y monitorear las sondas de forma remota y en tiempo real. Su eficiencia, bajo consumo y versatilidad la convierten en la opción ideal para implementar soluciones de monitoreo distribuido.',
      alt: 'Raspberry Pi 4 Model B',
      thumbnailUrl: `${import.meta.env.BASE_URL}images/raspberry-pi-4.jpg`
    },
    {
      id: '2',
      url: `${import.meta.env.BASE_URL}images/sonda-inspector-campo.jpg`,
      description: 'Así lucen las sondas Inspector instaladas en campo. Cada dispositivo está basado en una Raspberry Pi 4 y ejecuta el software sincronizado con OpenBalena, permitiendo el monitoreo remoto y la gestión centralizada del rendimiento de la red.',
      alt: 'Sonda Inspector instalada en campo',
      thumbnailUrl: `${import.meta.env.BASE_URL}images/sonda-inspector-campo.jpg`
    },
    {
      id: '3',
      url: `${import.meta.env.BASE_URL}images/modem-arris-tg2482.jpg`,
      description: 'En redes HFC, las sondas Inspector se conectan directamente al cablemódem Arris TG2482. Este dispositivo actúa como punto de referencia para medir niveles, latencias y calidad del servicio en tiempo real, permitiendo un monitoreo preciso del estado de la red.',
      alt: 'Módem Arris TG2482',
      thumbnailUrl: `${import.meta.env.BASE_URL}images/modem-arris-tg2482.jpg`
    },
    {
      id: '4',
      url: `${import.meta.env.BASE_URL}images/ont-huawei.jpg`,
      description: 'Esta ONT Huawei es utilizada en redes GPON para ofrecer conectividad de alta velocidad mediante fibra óptica, permitiendo el enlace directo entre el cliente y la red óptica pasiva del operador.',
      alt: 'ONT Huawei GPON',
      thumbnailUrl: `${import.meta.env.BASE_URL}images/ont-huawei.jpg`
    },
    {
      id: '5',
      url: `${import.meta.env.BASE_URL}images/tecnico-tigo.jpg`,
      description: 'El técnico de Tigo se encarga de realizar la instalación, verificación y reparación de las sondas en campo, garantizando que cada dispositivo quede correctamente conectado y funcionando para el monitoreo en tiempo real.',
      alt: 'Técnico de Tigo',
      thumbnailUrl: `${import.meta.env.BASE_URL}images/tecnico-tigo.jpg`
    }
  ];

  const handleImageClick = (image: ImageItem) => {
    const index = images.findIndex(img => img.id === image.id);
    setSelectedImageIndex(index);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedImageIndex(null);
  };

  const handlePrevious = () => {
    if (selectedImageIndex !== null && selectedImageIndex > 0) {
      setSelectedImageIndex(selectedImageIndex - 1);
    }
  };

  const handleNext = () => {
    if (selectedImageIndex !== null && selectedImageIndex < images.length - 1) {
      setSelectedImageIndex(selectedImageIndex + 1);
    }
  };

  const currentImage = selectedImageIndex !== null ? images[selectedImageIndex] : null;

  return (
    <div className="dashboard">
      <Sidebar />
      <main className="dashboard-body">
        <div className="images-dashboard">
          <div className="images-header">
            <h1 className="images-title">Imágenes</h1>
            <p className="images-subtitle">Galería de imágenes del sistema</p>
          </div>
          <div className="images-container">
            {images.length > 0 ? (
              images.map((image) => (
                <div
                  key={image.id}
                  className="image-card"
                  onClick={() => handleImageClick(image)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleImageClick(image);
                    }
                  }}
                  aria-label={`Ver imagen: ${image.alt || image.description}`}
                >
                  <div className="image-card-thumbnail">
                    <img
                      src={image.thumbnailUrl || image.url}
                      alt={image.alt || image.description}
                      className="image-thumbnail"
                      loading="lazy"
                    />
                  </div>
                  {image.description && (
                    <div className="image-card-description">
                      <p className="image-card-text">
                        {image.description.length > 100
                          ? `${image.description.substring(0, 100)}...`
                          : image.description}
                      </p>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="images-placeholder">
                <p>Las imágenes se mostrarán aquí</p>
              </div>
            )}
          </div>
        </div>
        {currentImage && selectedImageIndex !== null && (
          <ImageModal
            isOpen={isModalOpen}
            onClose={handleCloseModal}
            imageUrl={currentImage.url}
            description={currentImage.description}
            imageAlt={currentImage.alt || currentImage.description}
            currentIndex={selectedImageIndex}
            totalImages={images.length}
            onPrevious={handlePrevious}
            onNext={handleNext}
          />
        )}
      </main>
    </div>
  );
};

export default DashboardImages;


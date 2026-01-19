import { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import styles from './ImageCarousel.module.css';

interface ImageCarouselProps {
    images: string[];
    interval?: number; // milliseconds
    sectionName: string;
    resumeDelay?: number; // milliseconds to wait before resuming auto-play
}

const ImageCarousel = ({ images, interval = 7000, sectionName, resumeDelay = 15000 }: ImageCarouselProps) => {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isAutoPlaying, setIsAutoPlaying] = useState(true);
    const timerRef = useRef<number | null>(null);
    const resumeTimerRef = useRef<number | null>(null);

    // Auto-play functionality
    useEffect(() => {
        if (isAutoPlaying && images.length > 1) {
            timerRef.current = window.setInterval(() => {
                setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
            }, interval);
        }

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, [isAutoPlaying, images.length, interval]);

    // Resume auto-play after inactivity
    const scheduleResume = () => {
        // Clear any existing resume timer
        if (resumeTimerRef.current) {
            clearTimeout(resumeTimerRef.current);
        }

        // Schedule auto-play to resume after resumeDelay
        resumeTimerRef.current = window.setTimeout(() => {
            setIsAutoPlaying(true);
        }, resumeDelay);
    };

    // Cleanup resume timer on unmount
    useEffect(() => {
        return () => {
            if (resumeTimerRef.current) {
                clearTimeout(resumeTimerRef.current);
            }
        };
    }, []);

    const handleManualInteraction = () => {
        setIsAutoPlaying(false);
        scheduleResume();
    };

    const goToPrevious = () => {
        handleManualInteraction();
        setCurrentIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
    };

    const goToNext = () => {
        handleManualInteraction();
        setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    };

    const goToSlide = (index: number) => {
        handleManualInteraction();
        setCurrentIndex(index);
    };

    if (images.length === 0) {
        return null;
    }

    return (
        <div className={styles.carouselContainer}>
            <div className={styles.carouselWrapper}>
                {/* Previous Button */}
                {images.length > 1 && (
                    <button
                        className={`${styles.navButton} ${styles.navButtonLeft}`}
                        onClick={goToPrevious}
                        aria-label="Imagen anterior"
                    >
                        <ChevronLeft size={24} />
                    </button>
                )}

                {/* Image Display */}
                <div className={styles.imageWrapper}>
                    <img
                        src={images[currentIndex]}
                        alt={`${sectionName} - Imagen ${currentIndex + 1}`}
                        className={styles.carouselImage}
                    />
                </div>

                {/* Next Button */}
                {images.length > 1 && (
                    <button
                        className={`${styles.navButton} ${styles.navButtonRight}`}
                        onClick={goToNext}
                        aria-label="Imagen siguiente"
                    >
                        <ChevronRight size={24} />
                    </button>
                )}
            </div>

            {/* Indicators */}
            {images.length > 1 && (
                <div className={styles.indicators}>
                    {images.map((_, index) => (
                        <button
                            key={index}
                            className={`${styles.indicator} ${index === currentIndex ? styles.indicatorActive : ''}`}
                            onClick={() => goToSlide(index)}
                            aria-label={`Ir a imagen ${index + 1}`}
                        />
                    ))}
                </div>
            )}

            {/* Image Counter */}
            {images.length > 1 && (
                <div className={styles.counter}>
                    {currentIndex + 1} / {images.length}
                </div>
            )}

            {/* Auto-play indicator */}
            {isAutoPlaying && images.length > 1 && (
                <div className={styles.autoPlayIndicator}>
                    ▶ Auto
                </div>
            )}
        </div>
    );
};

export default ImageCarousel;

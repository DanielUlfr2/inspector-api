import React from 'react';
import './HeroBanner.css';

const HeroBanner = () => {
  return (
    <div className="hero-banner">
      <div className="hero-content">
        <h1 className="hero-headline">
          Monitoreo inteligente de sondas y dispositivos en tiempo real.
        </h1>
        <p className="hero-subtitle">
          Sincronizado con dispositivos OpenBalena
        </p>
      </div>
      <div className="hero-visual">
        <div className="signal-waves">
          <div className="wave-container">
            <svg className="wave-svg" viewBox="0 0 400 200" preserveAspectRatio="none">
              <defs>
                <linearGradient id="waveGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#0033A0" stopOpacity="0.8" />
                  <stop offset="50%" stopColor="#009FE3" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#0033A0" stopOpacity="0.8" />
                </linearGradient>
                <linearGradient id="waveGradient2" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#009FE3" stopOpacity="0.6" />
                  <stop offset="50%" stopColor="#0033A0" stopOpacity="0.8" />
                  <stop offset="100%" stopColor="#009FE3" stopOpacity="0.6" />
                </linearGradient>
                <linearGradient id="waveGradient3" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#0033A0" stopOpacity="0.4" />
                  <stop offset="50%" stopColor="#009FE3" stopOpacity="0.7" />
                  <stop offset="100%" stopColor="#0033A0" stopOpacity="0.4" />
                </linearGradient>
              </defs>
              <path
                className="wave-path wave-1"
                d="M0,100 Q100,50 200,100 T400,100 L400,200 L0,200 Z"
                fill="url(#waveGradient1)"
              />
              <path
                className="wave-path wave-2"
                d="M0,120 Q100,70 200,120 T400,120 L400,200 L0,200 Z"
                fill="url(#waveGradient2)"
              />
              <path
                className="wave-path wave-3"
                d="M0,140 Q100,90 200,140 T400,140 L400,200 L0,200 Z"
                fill="url(#waveGradient3)"
              />
            </svg>
          </div>
          <div className="signal-dots">
            <div className="dot dot-1"></div>
            <div className="dot dot-2"></div>
            <div className="dot dot-3"></div>
            <div className="dot dot-4"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroBanner;


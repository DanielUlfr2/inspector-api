import React from "react";
import "../styles/dashboard.css";
import Sidebar from "../components/Sidebar";
import "./DashboardImages.css";

const DashboardImages = () => {
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
            {/* Las imágenes se agregarán aquí */}
            <div className="images-placeholder">
              <p>Las imágenes se mostrarán aquí</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardImages;


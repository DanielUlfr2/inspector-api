
import React from "react";
import "../styles/dashboard.css";
import { useUser } from "../context/UserContext";
import RecordTable from "../components/RecordTable";
import Sidebar from "../components/Sidebar";
import HeroBanner from "../components/HeroBanner";

const DashboardDB = () => {
  const { nombre, rol, foto, token } = useUser();

  return (
    <div className="dashboard">
      <Sidebar />
      <main className="dashboard-body">
        <HeroBanner />
        <RecordTable />
      </main>
    </div>
  );
};

export default DashboardDB;

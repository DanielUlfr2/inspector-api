
import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import DashboardDB from "./pages/DashboardDB";
import EditProfile from "./pages/EditProfile";
import ViewProfile from "./pages/ViewProfile";
import ChangePhoto from "./pages/ChangePhoto";
import ChangePassword from "./pages/ChangePassword";
import { UserProvider, useUser } from "./context/UserContext";

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { token } = useUser();
  return token ? children : <Navigate to="/" />;
};

const App = () => {
  return (
    <UserProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardDB />
              </ProtectedRoute>
            }
          />
          <Route
            path="/editar-perfil"
            element={
              <ProtectedRoute>
                <EditProfile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/ver-perfil"
            element={
              <ProtectedRoute>
                <ViewProfile />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cambiar-foto"
            element={
              <ProtectedRoute>
                <ChangePhoto />
              </ProtectedRoute>
            }
          />
          <Route
            path="/cambiar-contraseña"
            element={
              <ProtectedRoute>
                <ChangePassword />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </UserProvider>
  );
};

export default App;

import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { BillingPage } from "../pages/BillingPage";
import { DashboardPage } from "../pages/DashboardPage";
import { DeveloperBidsPage } from "../pages/DeveloperBidsPage";
import { LoginPage } from "../pages/LoginPage";
import { PlanningDocumentsPage } from "../pages/PlanningDocumentsPage";
import { ProjectDetailsPage } from "../pages/ProjectDetailsPage";
import { ProjectsPage } from "../pages/ProjectsPage";
import { RegisterPage } from "../pages/RegisterPage";
import { ResidentPortalPage } from "../pages/ResidentPortalPage";
import { ResidentsPage } from "../pages/ResidentsPage";
import { SignaturesPage } from "../pages/SignaturesPage";
import { WorkflowPage } from "../pages/WorkflowPage";

function PrivateLayout() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/projects" element={<ProjectsPage />} />
        <Route path="/projects/:projectId" element={<ProjectDetailsPage />} />
        <Route path="/residents" element={<ResidentsPage />} />
        <Route path="/signatures" element={<SignaturesPage />} />
        <Route path="/workflow" element={<WorkflowPage />} />
        <Route path="/bids" element={<DeveloperBidsPage />} />
        <Route path="/planning" element={<PlanningDocumentsPage />} />
        <Route path="/billing" element={<BillingPage />} />
        <Route path="/resident-portal" element={<ResidentPortalPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

export function AppRoutes() {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <p style={{ padding: 24 }}>Loading...</p>;
  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/" replace /> : <RegisterPage />}
      />
      <Route path="/*" element={<PrivateLayout />} />
    </Routes>
  );
}

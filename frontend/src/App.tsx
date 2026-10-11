import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { Navbar } from "./components/Navbar";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { Documents } from "./pages/Documents";
import { DocumentDetail } from "./pages/DocumentDetail";
import { Workflow } from "./pages/Workflow";
import { Audit } from "./pages/Audit";
import { Search } from "./pages/Search";

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-500 text-sm">
        Verifying secure enterprise session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col">
      <Navbar />
      <main className="flex-1 pb-16">{children}</main>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedLayout>
                <Dashboard />
              </ProtectedLayout>
            }
          />
          <Route
            path="/documents"
            element={
              <ProtectedLayout>
                <Documents />
              </ProtectedLayout>
            }
          />
          <Route
            path="/documents/:id"
            element={
              <ProtectedLayout>
                <DocumentDetail />
              </ProtectedLayout>
            }
          />
          <Route
            path="/workflow"
            element={
              <ProtectedLayout>
                <Workflow />
              </ProtectedLayout>
            }
          />
          <Route
            path="/audit"
            element={
              <ProtectedLayout>
                <Audit />
              </ProtectedLayout>
            }
          />
          <Route
            path="/search"
            element={
              <ProtectedLayout>
                <Search />
              </ProtectedLayout>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

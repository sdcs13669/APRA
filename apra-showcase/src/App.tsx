import { Routes, Route, Navigate } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import Footer from "./components/layout/Footer";
import HomePage from "./pages/HomePage";
import PrinciplePage from "./pages/PrinciplePage";
import DashboardPage from "./pages/DashboardPage";
import ReplayPage from "./pages/ReplayPage";

export default function App() {
  return (
    <div className="relative min-h-screen" style={{ backgroundColor: "#F8FAFC", color: "#1E293B" }}>
      <div className="relative z-10">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/principle" element={<PrinciplePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/replay" element={<ReplayPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </div>
  );
}

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import PlatformNav from './components/layout/PlatformNav';
import Landing from './pages/Landing';
import PlatformHome from './pages/platform/PlatformHome';
import VulnScannerPage from './pages/platform/VulnScannerPage';
import SQLInjectionPage from './pages/platform/SQLInjectionPage';
import XSSScannerPage from './pages/platform/XSSScannerPage';

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <PlatformNav />
      <main className="flex-1">{children}</main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<Layout><PlatformHome /></Layout>} />
        <Route path="/dashboard/vuln-scanner"  element={<Layout><VulnScannerPage /></Layout>} />
        <Route path="/dashboard/sql-injection" element={<Layout><SQLInjectionPage /></Layout>} />
        <Route path="/dashboard/xss-scanner"   element={<Layout><XSSScannerPage /></Layout>} />
      </Routes>
    </BrowserRouter>
  );
}

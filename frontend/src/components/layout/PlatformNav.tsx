import { NavLink } from 'react-router-dom';
import { Code, Syringe, Zap, Menu, X, LayoutDashboard } from 'lucide-react';
import { useState } from 'react';
import SecureScopeLogo from '../SecureScopeLogo';

const navItems = [
  { to: '/dashboard',               label: 'Dashboard',    icon: LayoutDashboard, exact: true  },
  { to: '/dashboard/vuln-scanner',  label: 'Vuln Scanner', icon: Code,            exact: false },
  { to: '/dashboard/sql-injection', label: 'SQL Injection',icon: Syringe,         exact: false },
  { to: '/dashboard/xss-scanner',   label: 'XSS Scanner',  icon: Zap,             exact: false },
];

export default function PlatformNav() {
  const [open, setOpen] = useState(false);

  return (
    <header className="border-b border-white/[0.06] bg-[#0a0a0f]/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">

          <NavLink to="/" className="flex items-center gap-2.5">
            <SecureScopeLogo size={26} />
            <span className="font-bold text-slate-100 text-sm tracking-tight">SecureScope</span>
          </NavLink>

          <nav className="hidden md:flex items-center gap-0.5">
            {navItems.map(({ to, label, icon: Icon, exact }) => (
              <NavLink key={to} to={to} end={exact}
                className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`}>
                <Icon size={14} />{label}
              </NavLink>
            ))}
          </nav>

          <button className="md:hidden p-2 rounded-lg text-slate-500 hover:text-slate-300 hover:bg-white/[0.05] transition-colors"
            onClick={() => setOpen(!open)}>
            {open ? <X size={18} /> : <Menu size={18} />}
          </button>
        </div>

        {open && (
          <nav className="md:hidden pb-3 space-y-0.5 border-t border-white/[0.06] pt-3">
            {navItems.map(({ to, label, icon: Icon, exact }) => (
              <NavLink key={to} to={to} end={exact} onClick={() => setOpen(false)}
                className={({ isActive }) => `nav-link ${isActive ? 'nav-link-active' : ''}`}>
                <Icon size={14} />{label}
              </NavLink>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
}

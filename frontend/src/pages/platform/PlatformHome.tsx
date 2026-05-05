import { useNavigate } from 'react-router-dom';
import { Code, Syringe, Zap, ArrowRight, Shield, FileText, Search, Globe } from 'lucide-react';

const tools = [
  {
    id: 'vuln-scanner',
    route: '/dashboard/vuln-scanner',
    icon: Code,
    accent: 'text-cyan-400',
    accentBg: 'bg-cyan-500/10',
    accentBorder: 'border-cyan-500/20',
    title: 'Vulnerability Scanner',
    category: 'SAST',
    description: 'Scan GitHub repositories for exposed secrets, outdated dependencies, missing security headers, and code vulnerabilities.',
    features: ['Exposed secrets detection', 'Dependency audit', 'Security headers check', 'Code vulnerability analysis'],
    badge: 'GitHub Repos',
  },
  {
    id: 'sql-injection',
    route: '/dashboard/sql-injection',
    icon: Syringe,
    accent: 'text-red-400',
    accentBg: 'bg-red-500/10',
    accentBorder: 'border-red-500/20',
    title: 'SQL Injection Tester',
    category: 'Web Security',
    description: 'Test web applications for SQL injection. Manual mode or Smart Crawl that auto-discovers all parameters.',
    features: ['Error-based detection', 'Union-based detection', 'Boolean-blind detection', 'Time-based detection'],
    badge: 'Manual + Smart Crawl',
  },
  {
    id: 'xss-scanner',
    route: '/dashboard/xss-scanner',
    icon: Zap,
    accent: 'text-amber-400',
    accentBg: 'bg-amber-500/10',
    accentBorder: 'border-amber-500/20',
    title: 'XSS Scanner',
    category: 'Web Security',
    description: 'Detect Cross-Site Scripting vulnerabilities. Reflected and stored XSS with smart parameter discovery.',
    features: ['Reflected XSS detection', 'Stored XSS patterns', 'Smart crawl mode', 'False positive reduction'],
    badge: 'Manual + Smart Crawl',
  },
];

const stats = [
  { label: 'Security Tools',      value: '3',          icon: Shield },
  { label: 'Vulnerability Types', value: '10+',        icon: Search },
  { label: 'Report Formats',      value: 'PDF + JSON', icon: FileText },
  { label: 'Scan Modes',          value: '2',          icon: Globe },
];

export default function PlatformHome() {
  const navigate = useNavigate();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-10">

      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
          <span className="text-xs text-slate-600 font-mono uppercase tracking-wider">Platform Dashboard</span>
        </div>
        <h1 className="text-3xl font-bold text-slate-100 tracking-tight">Security Testing Platform</h1>
        <p className="text-slate-500 text-sm max-w-lg">
          3 production-grade tools. Smart parameter discovery. Professional PDF reports.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map(({ label, value, icon: Icon }) => (
          <div key={label} className="stat-card">
            <Icon size={14} className="text-slate-700 mb-1" />
            <p className="text-xl font-bold text-slate-100 font-mono">{value}</p>
            <p className="text-xs text-slate-600">{label}</p>
          </div>
        ))}
      </div>

      {/* Tool cards */}
      <div>
        <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-4">Available Tools</p>
        <div className="grid md:grid-cols-3 gap-4">
          {tools.map(({ id, route, icon: Icon, accent, accentBg, accentBorder, title, category, description, features, badge }) => (
            <div key={id} className="card-hover p-6 flex flex-col group">
              <div className="flex items-start justify-between mb-5">
                <div className={`w-9 h-9 ${accentBg} border ${accentBorder} rounded-xl flex items-center justify-center`}>
                  <Icon size={16} className={accent} />
                </div>
                <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${accentBg} ${accentBorder} ${accent}`}>
                  {badge}
                </span>
              </div>
              <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">{category}</p>
              <h3 className="text-base font-bold text-slate-100 mb-2 tracking-tight">{title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed mb-4 flex-1">{description}</p>
              <ul className="space-y-1.5 mb-5">
                {features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-slate-600">
                    <span className="w-1 h-1 bg-cyan-500/50 rounded-full shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => navigate(route)}
                className="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold
                           border border-white/[0.07] text-slate-400 hover:text-slate-100 hover:border-white/[0.15]
                           hover:bg-white/[0.03] transition-all duration-200"
              >
                Open Tool
                <ArrowRight size={13} className="group-hover:translate-x-0.5 transition-transform duration-200" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Demo notice */}
      <div className="card p-4 flex items-start gap-3">
        <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shrink-0 mt-1.5" />
        <div>
          <p className="text-xs font-semibold text-slate-400 mb-0.5">Demo Target Available</p>
          <p className="text-xs text-slate-600">
            Vulnerable test app at{' '}
            <code className="font-mono text-slate-500 bg-white/[0.04] px-1.5 py-0.5 rounded">http://localhost:8888</code>
            {' '}— use it to test all 3 tools and see real results.
          </p>
        </div>
      </div>
    </div>
  );
}

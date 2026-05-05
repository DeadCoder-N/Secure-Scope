import { useNavigate } from 'react-router-dom';
import { Code, Syringe, Zap, ArrowRight, Shield, FileText, Search } from 'lucide-react';

const tools = [
  {
    id: 'vuln-scanner',
    route: '/vuln-scanner',
    icon: Code,
    iconBg: 'bg-blue-600',
    title: 'Vulnerability Scanner',
    category: 'SAST Tool',
    description:
      'Scan any GitHub repository for exposed secrets, outdated dependencies, missing security headers, and code vulnerabilities. Generates a full PDF report.',
    features: ['Exposed secrets detection', 'Dependency audit', 'Security headers check', 'Code vulnerability analysis'],
    badge: 'GitHub Repos',
    badgeColor: 'bg-blue-50 text-blue-700',
  },
  {
    id: 'sql-injection',
    route: '/sql-injection',
    icon: Syringe,
    iconBg: 'bg-red-600',
    title: 'SQL Injection Tester',
    category: 'Web Security',
    description:
      'Test web applications for SQL injection vulnerabilities. Supports manual mode and smart crawl mode that auto-discovers all parameters.',
    features: ['Error-based detection', 'Union-based detection', 'Boolean blind detection', 'Time-based detection'],
    badge: 'Manual + Smart Crawl',
    badgeColor: 'bg-red-50 text-red-700',
  },
  {
    id: 'xss-scanner',
    route: '/xss-scanner',
    icon: Zap,
    iconBg: 'bg-amber-500',
    title: 'XSS Scanner',
    category: 'Web Security',
    description:
      'Detect Cross-Site Scripting vulnerabilities in web applications. Supports manual mode and smart crawl mode for automatic parameter discovery.',
    features: ['Reflected XSS detection', 'Stored XSS detection', 'Smart crawl mode', 'Fix recommendations'],
    badge: 'Manual + Smart Crawl',
    badgeColor: 'bg-amber-50 text-amber-700',
  },
];

const stats = [
  { label: 'Security Tools', value: '3', icon: Shield },
  { label: 'Vulnerability Types', value: '10+', icon: Search },
  { label: 'Report Formats', value: 'PDF + JSON', icon: FileText },
];

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10 space-y-10">

      {/* Hero */}
      <div className="text-center space-y-4 py-6">
        <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 text-sm font-medium px-4 py-1.5 rounded-full border border-blue-100">
          <Shield size={14} />
          Web Application Security Testing Platform
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 leading-tight">
          Find vulnerabilities before<br />
          <span className="text-blue-600">attackers do</span>
        </h1>
        <p className="text-slate-500 text-lg max-w-2xl mx-auto">
          SecureScope provides 3 production-grade security testing tools with automated scanning,
          smart parameter discovery, and professional PDF reports.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {stats.map(({ label, value, icon: Icon }) => (
          <div key={label} className="card p-5 text-center">
            <Icon size={20} className="text-blue-600 mx-auto mb-2" />
            <p className="text-2xl font-bold text-slate-900">{value}</p>
            <p className="text-sm text-slate-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Tool cards */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-5">Security Tools</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {tools.map(({ id, route, icon: Icon, iconBg, title, category, description, features, badge, badgeColor }) => (
            <div key={id} className="card p-6 flex flex-col hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className={`w-11 h-11 ${iconBg} rounded-xl flex items-center justify-center`}>
                  <Icon size={20} className="text-white" />
                </div>
                <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${badgeColor}`}>
                  {badge}
                </span>
              </div>

              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">{category}</p>
              <h3 className="text-lg font-bold text-slate-900 mb-2">{title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed mb-4 flex-1">{description}</p>

              <ul className="space-y-1.5 mb-5">
                {features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-xs text-slate-600">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => navigate(route)}
                className="btn-primary w-full justify-center text-sm"
              >
                Open Tool
                <ArrowRight size={15} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Demo target notice */}
      <div className="card p-5 bg-amber-50 border-amber-200">
        <div className="flex items-start gap-3">
          <div className="w-8 h-8 bg-amber-100 rounded-lg flex items-center justify-center shrink-0">
            <Shield size={16} className="text-amber-600" />
          </div>
          <div>
            <p className="font-semibold text-amber-900 text-sm">Demo Target Available</p>
            <p className="text-amber-700 text-sm mt-0.5">
              A vulnerable test application is running at{' '}
              <code className="font-mono bg-amber-100 px-1.5 py-0.5 rounded text-xs">http://localhost:8888</code>.
              Use it to test all 3 tools and see real results during your demo.
            </p>
          </div>
        </div>
      </div>

    </div>
  );
}

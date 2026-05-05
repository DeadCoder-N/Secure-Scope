import { useNavigate } from 'react-router-dom';
import { ArrowRight, Code, Syringe, Zap, FileText } from 'lucide-react';
import SecureScopeLogo from '../components/SecureScopeLogo';

const tools = [
  { icon: Code,    label: 'Vulnerability Scanner', desc: 'Secrets · Deps · Headers · SAST' },
  { icon: Syringe, label: 'SQL Injection Tester',  desc: 'Error · Union · Blind · Time' },
  { icon: Zap,     label: 'XSS Scanner',           desc: 'Reflected · Stored · Smart Crawl' },
];

const stats = [
  { value: '3',         label: 'Security Tools' },
  { value: '4',         label: 'Detection Methods' },
  { value: 'PDF+JSON',  label: 'Report Formats' },
  { value: 'OWASP',     label: 'Standard' },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col items-center justify-center">
      <div className="landing-glow" />

      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 py-20 text-center space-y-10">

        {/* Badge */}
        <div className="inline-flex items-center gap-2 border border-cyan-500/20 bg-cyan-500/[0.06] px-4 py-1.5 rounded-full">
          <SecureScopeLogo size={14} />
          <span className="text-xs font-semibold text-cyan-400 tracking-wide uppercase">
            Web Application Security Testing Platform
          </span>
        </div>

        {/* Hero */}
        <div className="space-y-5">
          <h1 className="text-5xl sm:text-6xl font-bold text-slate-100 leading-tight tracking-tight">
            Find vulnerabilities<br />
            <span className="text-cyan-400">before attackers do.</span>
          </h1>
          <p className="text-slate-500 text-lg max-w-xl mx-auto leading-relaxed">
            3 production-grade security tools. Smart parameter discovery.
            Real-time scan logs. Professional PDF reports.
          </p>
        </div>

        {/* CTA */}
        <button
          onClick={() => navigate('/dashboard')}
          className="inline-flex items-center gap-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950
                     font-bold px-8 py-3.5 rounded-xl transition-all duration-200 text-sm
                     glow-cyan group"
        >
          Open SecureScope
          <ArrowRight size={16} className="group-hover:translate-x-0.5 transition-transform duration-200" />
        </button>

        {/* Tool pills */}
        <div className="flex flex-wrap justify-center gap-3">
          {tools.map(({ icon: Icon, label, desc }) => (
            <div key={label}
              className="flex items-center gap-2.5 card px-4 py-2.5">
              <Icon size={13} className="text-slate-600" />
              <div className="text-left">
                <p className="text-xs font-semibold text-slate-300">{label}</p>
                <p className="text-xs text-slate-600">{desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-3">
          {stats.map(({ value, label }) => (
            <div key={label} className="card p-4">
              <p className="text-lg font-bold text-cyan-400 font-mono">{value}</p>
              <p className="text-xs text-slate-600 mt-0.5">{label}</p>
            </div>
          ))}
        </div>

        {/* Demo notice */}
        <div className="card p-3.5 flex items-center gap-3">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shrink-0" />
          <p className="text-xs text-slate-600 text-left">
            Demo target at{' '}
            <code className="font-mono text-slate-500 bg-white/[0.04] px-1.5 py-0.5 rounded">
              http://localhost:8888
            </code>
            {' '}— intentionally vulnerable app for live scanning demos.
          </p>
        </div>

        <div className="flex items-center justify-center gap-2">
          <FileText size={11} className="text-slate-700" />
          <p className="text-xs text-slate-700">
            SecureScope · React + Flask · For educational purposes only
          </p>
        </div>
      </div>
    </div>
  );
}

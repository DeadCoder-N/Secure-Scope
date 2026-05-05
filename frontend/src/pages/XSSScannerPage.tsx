import { useState } from 'react';
import { Zap, Play, AlertCircle, Globe, Link } from 'lucide-react';
import ScanProgress from '../components/shared/ScanProgress';
import VulnCard from '../components/shared/VulnCard';
import DownloadButtons from '../components/shared/DownloadButtons';
import SeverityBadge from '../components/shared/SeverityBadge';

const API = 'http://localhost:5003';

interface Vuln {
  type: string;
  severity: string;
  url?: string;
  parameter?: string;
  payload?: string;
  evidence?: string;
  fix_prompt?: string;
  owasp?: string;
  cwe?: string;
}

interface ScanResult {
  scan_id: string;
  target: string;
  scan_mode: string;
  total_vulnerabilities: number;
  params_tested?: number;
  severity_breakdown: Record<string, number>;
  vulnerabilities: Vuln[];
}

export default function XSSScannerPage() {
  const [target, setTarget] = useState('');
  const [scanMode, setScanMode] = useState<'manual' | 'smart'>('manual');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ step: '', percent: 0 });
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState('');

  const manualSteps = [
    { step: 'Parsing URL parameters...', percent: 20 },
    { step: 'Sending control request...', percent: 35 },
    { step: 'Testing reflected XSS payloads...', percent: 65 },
    { step: 'Checking stored XSS patterns...', percent: 85 },
    { step: 'Verifying results...', percent: 95 },
  ];

  const smartSteps = [
    { step: 'Crawling target website...', percent: 15 },
    { step: 'Discovering parameters...', percent: 30 },
    { step: 'Testing reflected XSS...', percent: 55 },
    { step: 'Checking stored patterns...', percent: 75 },
    { step: 'Verifying findings...', percent: 92 },
  ];

  async function runScan() {
    if (!target.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    const steps = scanMode === 'smart' ? smartSteps : manualSteps;
    let i = 0;
    const interval = setInterval(() => {
      if (i < steps.length) { setProgress(steps[i]); i++; }
    }, 1800);

    try {
      const res = await fetch(`${API}/api/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target.trim(), scan_mode: scanMode }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Scan failed');
      setResult(data);
      setProgress({ step: 'Scan complete!', percent: 100 });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Scan failed');
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  }

  function downloadJSON() {
    if (!result?.scan_id) return;
    window.open(`${API}/api/download?scan_id=${result.scan_id}&format=json`, '_blank');
  }

  function downloadPDF() {
    if (!result?.scan_id) return;
    window.open(`${API}/api/download?scan_id=${result.scan_id}&format=pdf`, '_blank');
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-amber-500 rounded-xl flex items-center justify-center">
          <Zap size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">XSS Scanner</h1>
          <p className="text-sm text-slate-500">Detect reflected and stored Cross-Site Scripting vulnerabilities</p>
        </div>
      </div>

      {/* Mode selector */}
      <div className="card p-1 flex gap-1 w-fit">
        <button
          onClick={() => setScanMode('manual')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            scanMode === 'manual' ? 'bg-amber-500 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Link size={15} /> Manual Mode
        </button>
        <button
          onClick={() => setScanMode('smart')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            scanMode === 'smart' ? 'bg-amber-500 text-white' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Globe size={15} /> Smart Crawl
        </button>
      </div>

      {/* Form */}
      <div className="card p-6 space-y-4">
        <div>
          <label className="label">
            {scanMode === 'manual' ? 'Target URL (with parameters)' : 'Base URL to crawl'}
          </label>
          <input
            className="input"
            placeholder={
              scanMode === 'manual'
                ? 'http://localhost:8888/search?q=hello'
                : 'http://localhost:8888'
            }
            value={target}
            onChange={e => setTarget(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && runScan()}
          />
          <p className="text-xs text-slate-400 mt-1.5">
            {scanMode === 'manual'
              ? 'URL must contain query parameters (e.g. ?q=hello&name=test)'
              : 'Smart Crawl will automatically discover all pages and parameters'}
          </p>
        </div>
        <button
          onClick={runScan}
          disabled={loading || !target.trim()}
          className="bg-amber-500 hover:bg-amber-600 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Play size={16} />
          {loading ? 'Scanning...' : 'Start Scan'}
        </button>
      </div>

      {loading && <ScanProgress step={progress.step} percent={progress.percent} />}

      {error && (
        <div className="card p-4 bg-red-50 border-red-200 flex items-start gap-3">
          <AlertCircle size={18} className="text-red-500 shrink-0 mt-0.5" />
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-5">
          <div className="card p-5">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className={`text-3xl font-bold ${result.total_vulnerabilities > 0 ? 'text-amber-500' : 'text-emerald-600'}`}>
                    {result.total_vulnerabilities}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">Vulnerabilities</p>
                </div>
                {result.params_tested != null && (
                  <div className="text-center">
                    <p className="text-3xl font-bold text-slate-900">{result.params_tested}</p>
                    <p className="text-xs text-slate-500 mt-0.5">Params Tested</p>
                  </div>
                )}
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(result.severity_breakdown).filter(([, v]) => v > 0).map(([sev, count]) => (
                    <div key={sev} className="text-center">
                      <SeverityBadge severity={sev} />
                      <p className="text-xs font-bold text-slate-700 mt-1">{count}</p>
                    </div>
                  ))}
                </div>
              </div>
              <DownloadButtons onDownloadPDF={downloadPDF} onDownloadJSON={downloadJSON} />
            </div>
          </div>

          {result.vulnerabilities.length > 0 ? (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Findings</h2>
              {result.vulnerabilities.map((v, i) => (
                <VulnCard
                  key={i}
                  index={i + 1}
                  type={v.type}
                  severity={v.severity}
                  parameter={v.parameter}
                  payload={v.payload}
                  evidence={v.evidence}
                  fixPrompt={v.fix_prompt}
                />
              ))}
            </div>
          ) : (
            <div className="card p-8 text-center">
              <p className="text-emerald-600 font-semibold text-lg">✅ No XSS vulnerabilities found</p>
              <p className="text-slate-500 text-sm mt-1">The target appears to be protected against XSS.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

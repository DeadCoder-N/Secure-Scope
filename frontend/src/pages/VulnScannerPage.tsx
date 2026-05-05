import { useState } from 'react';
import { Code, Play, AlertCircle } from 'lucide-react';
import ScanProgress from '../components/shared/ScanProgress';
import VulnCard from '../components/shared/VulnCard';
import DownloadButtons from '../components/shared/DownloadButtons';
import SeverityBadge from '../components/shared/SeverityBadge';

const API = 'http://localhost:5001';

interface ScanResult {
  scan_id: string;
  target: string;
  scan_type: string;
  scan_date: string;
  total_vulnerabilities: number;
  risk_score: number;
  risk_level: string;
  severity_breakdown: Record<string, number>;
  vulnerabilities: Vuln[];
}

interface Vuln {
  type: string;
  severity: string;
  file?: string;
  line?: number;
  description?: string;
  evidence?: string;
  parameter?: string;
  payload?: string;
  fix_prompt?: string;
  secret_type?: string;
  package?: string;
  header?: string;
}

export default function VulnScannerPage() {
  const [target, setTarget] = useState('');
  const [scanType, setScanType] = useState('auto');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState({ step: '', percent: 0 });
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState('');

  const steps = [
    { step: 'Cloning repository...', percent: 15 },
    { step: 'Scanning for secrets...', percent: 35 },
    { step: 'Checking dependencies...', percent: 55 },
    { step: 'Analyzing code...', percent: 75 },
    { step: 'Checking configurations...', percent: 90 },
    { step: 'Generating report...', percent: 98 },
  ];

  async function runScan() {
    if (!target.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    let i = 0;
    const interval = setInterval(() => {
      if (i < steps.length) {
        setProgress(steps[i]);
        i++;
      }
    }, 1800);

    try {
      const res = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target.trim(), scan_type: scanType }),
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

  const riskColor = (level: string) => {
    const m: Record<string, string> = { CRITICAL: 'text-red-600', HIGH: 'text-orange-500', MEDIUM: 'text-amber-500', LOW: 'text-emerald-500' };
    return m[level] ?? 'text-slate-600';
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
          <Code size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Vulnerability Scanner</h1>
          <p className="text-sm text-slate-500">Scan GitHub repos for secrets, outdated deps, and code vulnerabilities</p>
        </div>
      </div>

      {/* Form */}
      <div className="card p-6 space-y-4">
        <div>
          <label className="label">Target</label>
          <input
            className="input"
            placeholder="https://github.com/user/repo  or  /local/path"
            value={target}
            onChange={e => setTarget(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && runScan()}
          />
        </div>
        <div>
          <label className="label">Scan Type</label>
          <select className="input" value={scanType} onChange={e => setScanType(e.target.value)}>
            <option value="auto">Auto Detect</option>
            <option value="github">GitHub Repository</option>
            <option value="local">Local Directory</option>
            <option value="web">Live Website</option>
          </select>
        </div>
        <div className="flex items-center gap-3 pt-1">
          <button onClick={runScan} disabled={loading || !target.trim()} className="btn-primary">
            <Play size={16} />
            {loading ? 'Scanning...' : 'Start Scan'}
          </button>
          <span className="text-xs text-slate-400">Tip: try <code className="bg-slate-100 px-1 rounded">http://localhost:8888</code> for live demo</span>
        </div>
      </div>

      {/* Progress */}
      {loading && <ScanProgress step={progress.step} percent={progress.percent} />}

      {/* Error */}
      {error && (
        <div className="card p-4 bg-red-50 border-red-200 flex items-start gap-3">
          <AlertCircle size={18} className="text-red-500 shrink-0 mt-0.5" />
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-5">
          {/* Summary bar */}
          <div className="card p-5">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-6">
                <div className="text-center">
                  <p className={`text-3xl font-bold ${riskColor(result.risk_level)}`}>{result.risk_score}</p>
                  <p className="text-xs text-slate-500 mt-0.5">Risk Score</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-slate-900">{result.total_vulnerabilities}</p>
                  <p className="text-xs text-slate-500 mt-0.5">Total Issues</p>
                </div>
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

          {/* Findings */}
          {result.vulnerabilities.length > 0 ? (
            <div className="space-y-2">
              <h2 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Findings</h2>
              {result.vulnerabilities.map((v, i) => (
                <VulnCard
                  key={i}
                  index={i + 1}
                  type={v.type}
                  severity={v.severity}
                  description={v.description}
                  evidence={v.evidence}
                  file={v.file}
                  line={v.line}
                  fixPrompt={v.fix_prompt}
                />
              ))}
            </div>
          ) : (
            <div className="card p-8 text-center">
              <p className="text-emerald-600 font-semibold text-lg">✅ No vulnerabilities found</p>
              <p className="text-slate-500 text-sm mt-1">The target appears to be clean.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

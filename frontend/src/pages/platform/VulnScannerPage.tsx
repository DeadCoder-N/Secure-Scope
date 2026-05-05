import { useState } from 'react';
import { Code, Play, AlertCircle } from 'lucide-react';
import ScanTerminal, { buildLog, type LogLine } from '../../components/shared/ScanTerminal';
import VulnCard from '../../components/shared/VulnCard';
import DownloadButtons from '../../components/shared/DownloadButtons';
import SeverityBadge from '../../components/shared/SeverityBadge';

const API = 'http://localhost:5001';

interface Vuln {
  type: string; severity: string; file?: string; line?: number;
  description?: string; evidence?: string; fix_prompt?: string;
}
interface ScanResult {
  scan_id: string; target: string; scan_type: string; scan_date: string;
  total_vulnerabilities: number; risk_score: number; risk_level: string;
  severity_breakdown: Record<string, number>; vulnerabilities: Vuln[];
}

const LOG_STEPS: { msg: string; type: LogLine['type']; pct: number }[] = [
  { msg: 'Initializing scanner modules...',          type: 'info',    pct: 8  },
  { msg: 'Cloning repository...',                    type: 'default', pct: 18 },
  { msg: 'Scanning for exposed secrets...',          type: 'info',    pct: 32 },
  { msg: 'Checking dependency manifests...',         type: 'info',    pct: 48 },
  { msg: 'Running static code analysis...',          type: 'info',    pct: 62 },
  { msg: 'Checking configuration files...',          type: 'info',    pct: 76 },
  { msg: 'Analyzing security headers...',            type: 'info',    pct: 88 },
  { msg: 'Generating report...',                     type: 'muted',   pct: 96 },
];

export default function VulnScannerPage() {
  const [target, setTarget]     = useState('');
  const [scanType, setScanType] = useState('auto');
  const [loading, setLoading]   = useState(false);
  const [logs, setLogs]         = useState<LogLine[]>([]);
  const [percent, setPercent]   = useState(0);
  const [result, setResult]     = useState<ScanResult | null>(null);
  const [error, setError]       = useState('');

  function pushLog(msg: string, type: LogLine['type'] = 'default') {
    setLogs(prev => [...prev, buildLog(msg, type)]);
  }

  async function runScan() {
    if (!target.trim()) return;
    setLoading(true); setError(''); setResult(null);
    setLogs([buildLog('Starting vulnerability scan...', 'info')]);
    setPercent(2);

    let stepIdx = 0;
    const interval = setInterval(() => {
      if (stepIdx < LOG_STEPS.length) {
        const s = LOG_STEPS[stepIdx];
        setLogs(prev => [...prev, buildLog(s.msg, s.type)]);
        setPercent(s.pct);
        stepIdx++;
      }
    }, 1600);

    try {
      const res  = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target.trim(), scan_type: scanType }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Scan failed');

      clearInterval(interval);
      const total = data.total_vulnerabilities ?? 0;
      pushLog(`Scan complete — ${total} issue${total !== 1 ? 's' : ''} found.`,
        total > 0 ? 'warn' : 'success');
      if (data.severity_breakdown?.CRITICAL > 0)
        pushLog(`${data.severity_breakdown.CRITICAL} CRITICAL issue(s) require immediate attention.`, 'error');
      setPercent(100);
      setResult(data);
    } catch (e: unknown) {
      clearInterval(interval);
      const msg = e instanceof Error ? e.message : 'Scan failed';
      pushLog(`Error: ${msg}`, 'error');
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const riskColor = (l: string) =>
    ({ CRITICAL: 'text-red-400', HIGH: 'text-orange-400', MEDIUM: 'text-yellow-400', LOW: 'text-green-400' }[l] ?? 'text-slate-400');

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-cyan-500/10 border border-cyan-500/20 rounded-xl flex items-center justify-center">
          <Code size={16} className="text-cyan-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Vulnerability Scanner</h1>
          <p className="text-xs text-slate-600">Scan GitHub repos for secrets, outdated deps, and code vulnerabilities</p>
        </div>
      </div>

      {/* Form */}
      <div className="card p-6 space-y-4">
        <div>
          <label className="label">Target</label>
          <input className="input" placeholder="https://github.com/user/repo  or  /local/path"
            value={target} onChange={e => setTarget(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && runScan()} />
        </div>
        <div>
          <label className="label">Scan Type</label>
          <select className="select" value={scanType} onChange={e => setScanType(e.target.value)}>
            <option value="auto">Auto Detect</option>
            <option value="github">GitHub Repository</option>
            <option value="local">Local Directory</option>
            <option value="web">Live Website</option>
          </select>
        </div>
        <div className="flex items-center gap-4 pt-1">
          <button onClick={runScan} disabled={loading || !target.trim()} className="btn-primary">
            <Play size={14} />
            {loading ? 'Scanning...' : 'Start Scan'}
          </button>
          <span className="text-xs text-slate-700">
            Try{' '}
            <code className="font-mono text-slate-600 bg-white/[0.04] px-1.5 py-0.5 rounded">
              http://localhost:8888
            </code>
            {' '}for live demo
          </span>
        </div>
      </div>

      {/* Terminal */}
      {logs.length > 0 && (
        <ScanTerminal logs={logs} percent={percent} running={loading} target={target} />
      )}

      {/* Error */}
      {error && (
        <div className="card p-4 border-red-500/20 bg-red-500/[0.05] flex items-start gap-3">
          <AlertCircle size={15} className="text-red-400 shrink-0 mt-0.5" />
          <p className="text-red-400 text-xs">{error}</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4 fade-in-up">
          {/* Summary */}
          <div className="card p-5">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-6">
                <div>
                  <p className={`text-3xl font-bold font-mono ${riskColor(result.risk_level)}`}>
                    {result.risk_score}
                  </p>
                  <p className="text-xs text-slate-600 mt-0.5">Risk Score</p>
                </div>
                <div>
                  <p className="text-3xl font-bold font-mono text-slate-100">{result.total_vulnerabilities}</p>
                  <p className="text-xs text-slate-600 mt-0.5">Total Issues</p>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(result.severity_breakdown)
                    .filter(([, v]) => v > 0)
                    .map(([sev, count]) => (
                      <div key={sev} className="text-center">
                        <SeverityBadge severity={sev} />
                        <p className="text-xs font-bold text-slate-500 mt-1 font-mono">{count}</p>
                      </div>
                    ))}
                </div>
              </div>
              <DownloadButtons
                onDownloadPDF={() => window.open(`${API}/api/download?scan_id=${result.scan_id}&format=pdf`, '_blank')}
                onDownloadJSON={() => window.open(`${API}/api/download?scan_id=${result.scan_id}&format=json`, '_blank')}
              />
            </div>
          </div>

          {/* Findings */}
          {result.vulnerabilities.length > 0 ? (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Findings</p>
              {result.vulnerabilities.map((v, i) => (
                <VulnCard key={i} index={i + 1} type={v.type} severity={v.severity}
                  description={v.description} evidence={v.evidence}
                  file={v.file} line={v.line} fixPrompt={v.fix_prompt} />
              ))}
            </div>
          ) : (
            <div className="card p-10 text-center">
              <p className="text-green-400 font-semibold">✓ No vulnerabilities found</p>
              <p className="text-slate-600 text-xs mt-1">The target appears to be clean.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

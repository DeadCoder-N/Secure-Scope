import { useState } from 'react';
import { Zap, Play, AlertCircle, Globe, Link } from 'lucide-react';
import ScanTerminal, { buildLog, type LogLine } from '../../components/shared/ScanTerminal';
import VulnCard from '../../components/shared/VulnCard';
import DownloadButtons from '../../components/shared/DownloadButtons';
import SeverityBadge from '../../components/shared/SeverityBadge';

const API = 'http://localhost:5003';

interface Vuln {
  type: string; severity: string; url?: string; parameter?: string;
  payload?: string; evidence?: string; fix_prompt?: string;
}
interface ScanResult {
  scan_id: string; target: string; scan_mode: string;
  total_vulnerabilities: number; params_tested?: number;
  severity_breakdown: Record<string, number>; vulnerabilities: Vuln[];
}

const MANUAL_STEPS: { msg: string; type: LogLine['type']; pct: number }[] = [
  { msg: 'Parsing URL parameters...',              type: 'info',    pct: 12 },
  { msg: 'Sending control marker request...',      type: 'muted',   pct: 25 },
  { msg: 'Testing reflected XSS payloads...',      type: 'info',    pct: 55 },
  { msg: 'Checking stored XSS patterns...',        type: 'info',    pct: 75 },
  { msg: 'Verifying — filtering false positives...',type: 'muted',  pct: 92 },
];
const SMART_STEPS: { msg: string; type: LogLine['type']; pct: number }[] = [
  { msg: 'Initializing crawler...',                type: 'info',    pct: 8  },
  { msg: 'Crawling target website...',             type: 'default', pct: 22 },
  { msg: 'Discovering URL parameters...',          type: 'info',    pct: 35 },
  { msg: 'Testing reflected XSS...',               type: 'info',    pct: 58 },
  { msg: 'Checking stored XSS patterns...',        type: 'info',    pct: 75 },
  { msg: 'Verifying — filtering false positives...',type: 'muted',  pct: 92 },
];

export default function XSSScannerPage() {
  const [target, setTarget]     = useState('');
  const [scanMode, setScanMode] = useState<'manual' | 'smart'>('manual');
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
    setLogs([buildLog(`Starting XSS scan — mode: ${scanMode}`, 'info')]);
    setPercent(2);

    const steps = scanMode === 'smart' ? SMART_STEPS : MANUAL_STEPS;
    let i = 0;
    const interval = setInterval(() => {
      if (i < steps.length) {
        const s = steps[i];
        setLogs(prev => [...prev, buildLog(s.msg, s.type)]);
        setPercent(s.pct);
        i++;
      }
    }, 1800);

    try {
      const res  = await fetch(`${API}/api/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target: target.trim(), scan_mode: scanMode }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Scan failed');

      clearInterval(interval);
      const total = data.total_vulnerabilities ?? 0;
      if (total > 0) {
        pushLog(`⚠ ${total} XSS vulnerability${total !== 1 ? 'ies' : 'y'} confirmed.`, 'warn');
        data.vulnerabilities?.forEach((v: Vuln) => {
          pushLog(`✓ ${v.type} on param '${v.parameter}' [${v.severity}]`, 'warn');
        });
      } else {
        pushLog('No XSS vulnerabilities detected.', 'success');
      }
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

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-10 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 bg-amber-500/10 border border-amber-500/20 rounded-xl flex items-center justify-center">
          <Zap size={16} className="text-amber-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">XSS Scanner</h1>
          <p className="text-xs text-slate-600">Reflected XSS · Stored XSS · False positive reduction</p>
        </div>
      </div>

      {/* Mode toggle */}
      <div className="card p-1 flex gap-1 w-fit">
        <button onClick={() => setScanMode('manual')}
          className={`mode-tab ${scanMode === 'manual' ? 'mode-tab-active' : ''}`}>
          <Link size={13} /> Manual
        </button>
        <button onClick={() => setScanMode('smart')}
          className={`mode-tab ${scanMode === 'smart' ? 'mode-tab-active' : ''}`}>
          <Globe size={13} /> Smart Crawl
        </button>
      </div>

      {/* Form */}
      <div className="card p-6 space-y-4">
        <div>
          <label className="label">
            {scanMode === 'manual' ? 'Target URL (with parameters)' : 'Base URL to crawl'}
          </label>
          <input className="input"
            placeholder={scanMode === 'manual' ? 'http://localhost:8888/search?q=hello' : 'http://localhost:8888'}
            value={target} onChange={e => setTarget(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && runScan()} />
          <p className="text-xs text-slate-700 mt-2">
            {scanMode === 'manual'
              ? 'URL must contain query parameters — e.g. ?q=hello'
              : 'Smart Crawl discovers all pages and parameters automatically'}
          </p>
        </div>
        <button onClick={runScan} disabled={loading || !target.trim()} className="btn-amber">
          <Play size={14} />
          {loading ? 'Scanning...' : 'Start Scan'}
        </button>
      </div>

      {logs.length > 0 && (
        <ScanTerminal logs={logs} percent={percent} running={loading} target={target} />
      )}

      {error && (
        <div className="card p-4 border-red-500/20 bg-red-500/[0.05] flex items-start gap-3">
          <AlertCircle size={15} className="text-red-400 shrink-0 mt-0.5" />
          <p className="text-red-400 text-xs">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4 fade-in-up">
          <div className="card p-5">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center gap-6">
                <div>
                  <p className={`text-3xl font-bold font-mono ${result.total_vulnerabilities > 0 ? 'text-amber-400' : 'text-green-400'}`}>
                    {result.total_vulnerabilities}
                  </p>
                  <p className="text-xs text-slate-600 mt-0.5">Vulnerabilities</p>
                </div>
                {result.params_tested != null && (
                  <div>
                    <p className="text-3xl font-bold font-mono text-slate-100">{result.params_tested}</p>
                    <p className="text-xs text-slate-600 mt-0.5">Params Tested</p>
                  </div>
                )}
                <div className="flex gap-2 flex-wrap">
                  {Object.entries(result.severity_breakdown).filter(([, v]) => v > 0).map(([sev, count]) => (
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

          {result.vulnerabilities.length > 0 ? (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Findings</p>
              {result.vulnerabilities.map((v, i) => (
                <VulnCard key={i} index={i + 1} type={v.type} severity={v.severity}
                  parameter={v.parameter} payload={v.payload} evidence={v.evidence}
                  fixPrompt={v.fix_prompt} />
              ))}
            </div>
          ) : (
            <div className="card p-10 text-center">
              <p className="text-green-400 font-semibold">✓ No XSS vulnerabilities found</p>
              <p className="text-slate-600 text-xs mt-1">The target appears to be protected.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

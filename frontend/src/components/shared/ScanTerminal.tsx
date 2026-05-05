import { useEffect, useRef, useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Circle } from 'lucide-react';

export interface LogLine {
  time: string;
  message: string;
  type: 'info' | 'success' | 'warn' | 'error' | 'muted' | 'default';
}

interface ScanTerminalProps {
  logs: LogLine[];
  percent: number;
  running: boolean;
  target?: string;
}

function now() {
  return new Date().toLocaleTimeString('en-US', { hour12: false });
}

export function buildLog(message: string, type: LogLine['type'] = 'default'): LogLine {
  return { time: now(), message, type };
}

export default function ScanTerminal({ logs, percent, running, target }: ScanTerminalProps) {
  const [collapsed, setCollapsed] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom as logs come in
  useEffect(() => {
    if (!collapsed) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, collapsed]);

  // Collapse when scan finishes
  useEffect(() => {
    if (!running && logs.length > 0) {
      const t = setTimeout(() => setCollapsed(true), 1200);
      return () => clearTimeout(t);
    }
  }, [running, logs.length]);

  const typeClass: Record<LogLine['type'], string> = {
    success: 'terminal-success',
    warn:    'terminal-warn',
    error:   'terminal-error',
    info:    'terminal-info',
    muted:   'terminal-muted',
    default: 'terminal-default',
  };

  const prefix: Record<LogLine['type'], string> = {
    success: '✓',
    warn:    '⚠',
    error:   '✗',
    info:    '→',
    muted:   ' ',
    default: ' ',
  };

  return (
    <div className="terminal fade-in-up">
      {/* Header bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-500/60" />
            <span className="w-3 h-3 rounded-full bg-yellow-500/60" />
            <span className="w-3 h-3 rounded-full bg-green-500/60" />
          </div>
          <div className="flex items-center gap-2">
            <Terminal size={13} className="text-slate-600" />
            <span className="text-xs text-slate-500 font-mono">
              {running ? (
                <span className="flex items-center gap-1.5">
                  <Circle size={6} className="text-cyan-400 fill-cyan-400 animate-pulse" />
                  SCANNING
                </span>
              ) : logs.length > 0 ? (
                <span className="flex items-center gap-1.5">
                  <Circle size={6} className="text-green-400 fill-green-400" />
                  COMPLETE
                </span>
              ) : 'TERMINAL'}
            </span>
            {target && (
              <span className="text-xs text-slate-600 font-mono truncate max-w-xs hidden sm:block">
                — {target}
              </span>
            )}
          </div>
        </div>
        {!running && logs.length > 0 && (
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-400 transition-colors"
          >
            {collapsed ? (
              <><ChevronDown size={14} /> View log</>
            ) : (
              <><ChevronUp size={14} /> Collapse</>
            )}
          </button>
        )}
      </div>

      {/* Log body */}
      {!collapsed && (
        <div className="p-4 space-y-0.5 max-h-72 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className={`terminal-line flex gap-3 ${typeClass[log.type]}`}>
              <span className="text-slate-700 shrink-0 select-none">[{log.time}]</span>
              <span className="shrink-0 w-3 text-center select-none">{prefix[log.type]}</span>
              <span>{log.message}</span>
            </div>
          ))}
          {running && (
            <div className="terminal-line terminal-muted flex gap-3">
              <span className="text-slate-700 shrink-0">[{now()}]</span>
              <span className="shrink-0 w-3" />
              <span className="cursor-blink">█</span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
      )}

      {/* Progress bar */}
      {running && (
        <div className="px-4 pb-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-slate-600 font-mono">Progress</span>
            <span className="text-xs text-cyan-400 font-mono font-semibold">{percent}%</span>
          </div>
          <div className="w-full bg-white/[0.05] rounded-full h-1 overflow-hidden">
            <div
              className="h-full rounded-full progress-bar transition-all duration-700 ease-out"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import SeverityBadge from './SeverityBadge';

interface VulnCardProps {
  index: number;
  type: string;
  severity: string;
  description?: string;
  evidence?: string;
  parameter?: string;
  payload?: string;
  file?: string;
  line?: number;
  fixPrompt?: string;
}

export default function VulnCard({
  index, type, severity, description, evidence,
  parameter, payload, file, line, fixPrompt,
}: VulnCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card overflow-hidden">
      <button
        className="w-full flex items-center justify-between p-4 text-left hover:bg-white/[0.02] transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="text-slate-700 font-mono text-xs w-6 shrink-0 select-none">
            {String(index).padStart(2, '0')}
          </span>
          <SeverityBadge severity={severity} />
          <span className="font-medium text-slate-200 text-sm truncate">{type}</span>
          {parameter && (
            <span className="text-xs text-slate-600 font-mono bg-white/[0.04] px-2 py-0.5 rounded border border-white/[0.06] hidden sm:block">
              {parameter}
            </span>
          )}
        </div>
        {expanded
          ? <ChevronUp size={14} className="text-slate-600 shrink-0" />
          : <ChevronDown size={14} className="text-slate-600 shrink-0" />
        }
      </button>

      {expanded && (
        <div className="border-t border-white/[0.06] p-4 space-y-3 text-sm fade-in-up">
          {description && (
            <div>
              <p className="label">Description</p>
              <p className="text-slate-400 text-xs leading-relaxed">{description}</p>
            </div>
          )}
          {evidence && (
            <div>
              <p className="label">Evidence</p>
              <p className="text-slate-400 font-mono text-xs bg-white/[0.03] p-2.5 rounded border border-white/[0.06] break-all">
                {evidence}
              </p>
            </div>
          )}
          {payload && (
            <div>
              <p className="label">Payload</p>
              <code className="text-xs bg-red-500/[0.08] text-red-400 px-2.5 py-1.5 rounded border border-red-500/20 block break-all font-mono">
                {payload}
              </code>
            </div>
          )}
          {file && (
            <div>
              <p className="label">Location</p>
              <p className="text-slate-500 font-mono text-xs">
                {file}{line ? ` : line ${line}` : ''}
              </p>
            </div>
          )}
          {fixPrompt && (
            <div className="bg-cyan-500/[0.06] border border-cyan-500/20 rounded-lg p-3">
              <p className="text-xs font-semibold text-cyan-400 mb-1.5">💡 How to Fix</p>
              <p className="text-cyan-300/70 text-xs leading-relaxed">{fixPrompt}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

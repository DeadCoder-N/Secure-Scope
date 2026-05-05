type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO' | string;

export default function SeverityBadge({ severity }: { severity: Severity }) {
  const s = severity?.toUpperCase();
  if (s === 'CRITICAL') return <span className="badge-critical">CRITICAL</span>;
  if (s === 'HIGH')     return <span className="badge-high">HIGH</span>;
  if (s === 'MEDIUM')   return <span className="badge-medium">MEDIUM</span>;
  if (s === 'INFO')     return <span className="badge-info">INFO</span>;
  return <span className="badge-low">LOW</span>;
}

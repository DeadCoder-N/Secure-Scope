interface ScanProgressProps {
  step: string;
  percent: number;
}

export default function ScanProgress({ step, percent }: ScanProgressProps) {
  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-600 font-medium">{step}</span>
        <span className="text-blue-600 font-mono font-semibold">{percent}%</span>
      </div>
      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-blue-600 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

import { Download, FileJson } from 'lucide-react';

interface DownloadButtonsProps {
  onDownloadPDF: () => void;
  onDownloadJSON: () => void;
  disabled?: boolean;
}

export default function DownloadButtons({ onDownloadPDF, onDownloadJSON, disabled }: DownloadButtonsProps) {
  return (
    <div className="flex gap-2">
      <button onClick={onDownloadJSON} disabled={disabled} className="btn-ghost">
        <FileJson size={14} />
        JSON
      </button>
      <button onClick={onDownloadPDF} disabled={disabled} className="btn-primary">
        <Download size={14} />
        PDF Report
      </button>
    </div>
  );
}

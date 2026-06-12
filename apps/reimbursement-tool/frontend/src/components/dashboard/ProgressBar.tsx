import { Loader2, CheckCircle } from 'lucide-react';
import { useProcessingStore } from '../../store/processingStore';

export function ProgressBar() {
  const { isProcessing, progress, lastMessage, exportFilename } = useProcessingStore();

  if (!isProcessing && !exportFilename) return null;

  const pct = progress.total > 0
    ? Math.round((progress.current / progress.total) * 100)
    : 0;

  return (
    <div className="card p-4">
      <div className="flex items-center gap-3 mb-3">
        {isProcessing ? (
          <Loader2 className="w-4 h-4 text-[#F47920] animate-spin flex-shrink-0" />
        ) : (
          <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
        )}
        <div className="flex-1">
          <div className="flex justify-between text-xs text-gray-500 mb-1.5">
            <span className="truncate">{lastMessage || (isProcessing ? 'Processing...' : 'Complete')}</span>
            <span className="flex-shrink-0 ml-2">
              {progress.current} / {progress.total}
            </span>
          </div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                isProcessing ? 'bg-[#F47920]' : 'bg-green-500'
              }`}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
        <span className="text-xs text-gray-500 flex-shrink-0 w-8 text-right">
          {pct}%
        </span>
      </div>

      {exportFilename && !isProcessing && (
        <div className="flex items-center justify-between pt-2 border-t border-gray-200">
          <span className="text-xs text-green-600">Export ready: {exportFilename}</span>
          <a
            href={`/api/export/${exportFilename}`}
            download={exportFilename}
            className="btn-primary text-xs px-3 py-1"
          >
            Download
          </a>
        </div>
      )}
    </div>
  );
}

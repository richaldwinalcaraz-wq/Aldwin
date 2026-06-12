import { FileDown, Loader2, Download } from 'lucide-react';
import { useExportList, downloadFile } from '../../hooks/useExport';
import { useExportGenerate } from '../../hooks/useProcessing';
import { useUploadStore } from '../../store/uploadStore';
import { useProcessingStore } from '../../store/processingStore';

export function DownloadCenter() {
  const { sessionId } = useUploadStore();
  const { isProcessing } = useProcessingStore();
  const { data: records = [], refetch } = useExportList();
  const generateExport = useExportGenerate();

  function handleGenerate() {
    generateExport.mutate(undefined, { onSuccess: () => refetch() });
  }

  if (!sessionId) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <FileDown className="w-10 h-10 text-gray-300 mb-3" />
        <p className="text-sm text-gray-500">No session active.</p>
        <p className="text-xs text-neutral-600 mt-1">Upload files first.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-700">Export History</p>
          <p className="text-xs text-gray-500 mt-0.5">
            Generate write-back Excel after sending is complete.
          </p>
        </div>
        <button
          className="btn-primary text-sm"
          disabled={isProcessing || generateExport.isPending}
          onClick={handleGenerate}
        >
          {generateExport.isPending ? (
            <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Generating...</>
          ) : (
            <><FileDown className="w-3.5 h-3.5" /> Generate Export</>
          )}
        </button>
      </div>

      {generateExport.isError && (
        <p className="text-xs text-red-400">{generateExport.error?.message}</p>
      )}

      {records.length === 0 ? (
        <div className="card p-8 text-center">
          <p className="text-sm text-gray-500">No exports yet.</p>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left text-gray-500 font-medium">File Name</th>
                <th className="px-4 py-3 text-left text-gray-500 font-medium">Processed Date</th>
                <th className="px-4 py-3 text-left text-gray-500 font-medium">Sent</th>
                <th className="px-4 py-3 text-left text-gray-500 font-medium">Failed</th>
                <th className="px-4 py-3 text-left text-gray-500 font-medium"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {records.map((rec) => (
                <tr key={rec.filename} className="table-row-hover">
                  <td className="px-4 py-3 font-mono text-gray-700">{rec.filename}</td>
                  <td className="px-4 py-3 text-gray-500">{rec.processedDate}</td>
                  <td className="px-4 py-3">
                    <span className="badge-green">{rec.totalSent}</span>
                  </td>
                  <td className="px-4 py-3">
                    {rec.failedRows > 0 ? (
                      <span className="badge-red">{rec.failedRows}</span>
                    ) : (
                      <span className="badge-gray">0</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      className="btn-secondary text-xs px-3 py-1 gap-1.5"
                      onClick={() => downloadFile(rec.filename)}
                    >
                      <Download className="w-3 h-3" /> Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

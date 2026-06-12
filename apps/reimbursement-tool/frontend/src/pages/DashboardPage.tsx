import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, CheckSquare, Send, FileDown, AlertCircle } from 'lucide-react';
import { StatsBar } from '../components/dashboard/StatsBar';
import { ProcessingTable } from '../components/dashboard/ProcessingTable';
import { ProgressBar } from '../components/dashboard/ProgressBar';
import { EmailPreviewModal } from '../components/preview/EmailPreviewModal';
import { useUploadStore } from '../store/uploadStore';
import { useProcessingStore } from '../store/processingStore';
import { useApproveSend, useExportGenerate } from '../hooks/useProcessing';
import { ProcessedRow } from '../types';
import { api } from '../lib/api';

export function DashboardPage() {
  const navigate = useNavigate();
  const { uploadResponse, sessionId, updateRow } = useUploadStore();
  const { isProcessing, exportFilename } = useProcessingStore();
  const [previewRow, setPreviewRow] = useState<ProcessedRow | null>(null);
  const { approveMutation, sendMutation } = useApproveSend();
  const exportMutation = useExportGenerate();

  if (!uploadResponse) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-10 h-10 text-gray-300 mb-3" />
        <p className="text-sm text-gray-500">No data loaded.</p>
        <button className="btn-primary mt-4" onClick={() => navigate('/')}>
          Upload Files
        </button>
      </div>
    );
  }

  const rows = uploadResponse.rows;
  const approvedCount = rows.filter((r) => r.approved).length;
  const sentCount = rows.filter((r) => r.sendStatus === 'SENT').length;

  function handleToggleApprove(rowIndex: number, approved: boolean) {
    updateRow(rowIndex, { approved });
    if (sessionId) {
      api.post('/process/approve', {
        sessionId,
        rowIndexes: [rowIndex],
        approveAll: false,
      }).catch(() => {});
    }
  }

  function handleApproveAll() {
    approveMutation.mutate({ approveAll: true });
    rows.forEach((r) => {
      if (r.validationStatus === 'READY' || r.validationStatus === 'NO_ACCESS') {
        updateRow(r.rowIndex, { approved: true });
      }
    });
  }

  function handleSend() {
    sendMutation.mutate();
  }

  function handleApproveFromModal(rowIndex: number) {
    handleToggleApprove(rowIndex, true);
  }

  function handleDenyFromModal(rowIndex: number) {
    handleToggleApprove(rowIndex, false);
    updateRow(rowIndex, { approved: false });
  }

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-[#1B3A8A]">Dashboard</h1>
          <p className="text-gray-500 text-sm mt-1">
            {rows.length} rows loaded · {approvedCount} approved
          </p>
        </div>

        <div className="flex items-center gap-3">
          {sentCount > 0 && !isProcessing && (
            <button
              className="btn-secondary"
              disabled={exportMutation.isPending}
              onClick={() => exportMutation.mutate()}
            >
              {exportMutation.isPending ? (
                <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Exporting...</>
              ) : (
                <><FileDown className="w-3.5 h-3.5" /> Export Excel</>
              )}
            </button>
          )}
          <button
            className="btn-secondary"
            disabled={isProcessing || approveMutation.isPending}
            onClick={handleApproveAll}
          >
            <CheckSquare className="w-3.5 h-3.5" />
            Approve All Ready
          </button>
          <button
            className="btn-primary"
            disabled={approvedCount === 0 || isProcessing}
            onClick={handleSend}
          >
            {isProcessing ? (
              <><Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing...</>
            ) : (
              <><Send className="w-3.5 h-3.5" /> Send {approvedCount > 0 ? `(${approvedCount})` : ''}</>
            )}
          </button>
        </div>
      </div>

      {/* Stats */}
      <StatsBar rows={rows} />

      {/* Progress (shown during processing) */}
      <ProgressBar />

      {/* Export ready notification */}
      {exportFilename && !isProcessing && (
        <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-700">Export ready: {exportFilename}</p>
          <a
            href={`/api/export/${exportFilename}`}
            download={exportFilename}
            className="btn-primary text-xs px-3 py-1.5"
          >
            Download
          </a>
        </div>
      )}

      {sendMutation.isError && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-4 h-4 text-red-600" />
          <p className="text-sm text-red-700">{sendMutation.error?.message}</p>
        </div>
      )}

      {/* Processing table */}
      <ProcessingTable
        rows={rows}
        onPreview={(row) => setPreviewRow(row)}
        onToggleApprove={handleToggleApprove}
      />

      {/* Email preview modal */}
      <EmailPreviewModal
        row={previewRow}
        onClose={() => setPreviewRow(null)}
        onApprove={handleApproveFromModal}
        onDeny={handleDenyFromModal}
      />
    </div>
  );
}

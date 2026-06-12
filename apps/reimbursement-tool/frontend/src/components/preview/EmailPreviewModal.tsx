import { useState, useEffect } from 'react';
import { X, Loader2, Paperclip, Mail } from 'lucide-react';
import { api } from '../../lib/api';
import { EmailPreview, ProcessedRow } from '../../types';
import { useUploadStore } from '../../store/uploadStore';

interface Props {
  row: ProcessedRow | null;
  onClose: () => void;
  onApprove: (rowIndex: number) => void;
  onDeny: (rowIndex: number) => void;
}

const TEMPLATE_LABELS: Record<string, string> = {
  standard: 'Standard',
  informational: 'Informational (No Access)',
  follow_up: 'Follow-Up (Past Due)',
  resubmission: 'Resubmission',
  priority: 'Priority (Urgent)',
};

export function EmailPreviewModal({ row, onClose, onApprove, onDeny }: Props) {
  const { sessionId } = useUploadStore();
  const [preview, setPreview] = useState<EmailPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!row || !sessionId) return;
    setLoading(true);
    setError(null);
    api
      .post<EmailPreview>(`/preview/email/${row.rowIndex}?sessionId=${sessionId}`)
      .then((r) => setPreview(r.data))
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [row, sessionId]);

  if (!row) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-3xl max-h-[90vh] flex flex-col bg-white border border-gray-200 rounded-xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-[#1B3A8A] rounded-t-xl">
          <div className="flex items-center gap-3">
            <Mail className="w-4 h-4 text-white/70" />
            <div>
              <p className="text-sm font-semibold text-white">{row.companyName}</p>
              <p className="text-xs text-white/60">Email Preview</p>
            </div>
          </div>
          <button className="p-1.5 text-white/60 hover:text-white hover:bg-white/10 rounded transition-colors" onClick={onClose}>
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto p-6">
          {loading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-5 h-5 text-[#F47920] animate-spin" />
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600 text-center py-8">{error}</p>
          )}

          {preview && !loading && (
            <div className="space-y-4">
              {/* Recipients */}
              <div className="grid grid-cols-3 gap-4">
                <RecipientField label="TO" values={[preview.to]} />
                <RecipientField label="CC" values={preview.cc} />
                <RecipientField label="BCC" values={preview.bcc} />
              </div>

              {/* Subject + template */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Subject</p>
                  <p className="text-sm text-gray-900 bg-gray-50 border border-gray-200 rounded px-3 py-2">
                    {preview.subject}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Template</p>
                  <p className="text-sm text-gray-900 bg-gray-50 border border-gray-200 rounded px-3 py-2">
                    {TEMPLATE_LABELS[preview.templateType] ?? preview.templateType}
                  </p>
                </div>
              </div>

              {/* PDF attachment */}
              {preview.hasPdf && preview.pdfFilename && (
                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Attachment</p>
                  <div className="flex items-center gap-2 px-3 py-2 bg-gray-50 border border-gray-200 rounded">
                    <Paperclip className="w-3.5 h-3.5 text-gray-500" />
                    <span className="text-sm text-gray-700">{preview.pdfFilename}</span>
                  </div>
                </div>
              )}

              {!preview.hasPdf && (
                <div className="px-3 py-2 bg-amber-50 border border-amber-200 rounded text-xs text-amber-700">
                  No PDF attachment — informational email only
                </div>
              )}

              {/* Email body preview */}
              <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Email Body</p>
                <div
                  className="bg-white border border-gray-200 rounded-lg overflow-auto max-h-64 text-sm"
                  dangerouslySetInnerHTML={{ __html: preview.bodyHtml }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
          <button
            className="btn-danger"
            onClick={() => { onDeny(row.rowIndex); onClose(); }}
          >
            Deny
          </button>
          <div className="flex gap-3">
            <button className="btn-secondary" onClick={onClose}>
              Close
            </button>
            <button
              className="btn-primary"
              onClick={() => { onApprove(row.rowIndex); onClose(); }}
              disabled={row.validationStatus === 'MISSING_PDF' || row.validationStatus === 'INVALID_EMAIL'}
            >
              Approve
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function RecipientField({ label, values }: { label: string; values: string[] }) {
  return (
    <div>
      <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">{label}</p>
      <div className="min-h-[36px] px-3 py-2 bg-gray-50 border border-gray-200 rounded text-xs text-gray-700 break-all">
        {values.length > 0 ? values.join(', ') : <span className="text-gray-300">—</span>}
      </div>
    </div>
  );
}

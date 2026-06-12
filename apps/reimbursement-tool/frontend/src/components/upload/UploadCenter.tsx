import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, ArrowRight, AlertCircle } from 'lucide-react';
import { ExcelDropzone } from './ExcelDropzone';
import { ZipDropzone } from './ZipDropzone';
import { useUpload } from '../../hooks/useUpload';
import { useUploadStore } from '../../store/uploadStore';

export function UploadCenter() {
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [zipFile, setZipFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const { mutate: upload, isPending } = useUpload();
  const { uploadError } = useUploadStore();

  function handleSubmit() {
    if (!excelFile || !zipFile) return;
    const formData = new FormData();
    formData.append('excel', excelFile);
    formData.append('zip', zipFile);
    upload(formData, {
      onSuccess: () => navigate('/dashboard'),
    });
  }

  const canSubmit = !!excelFile && !!zipFile && !isPending;

  return (
    <div className="p-8 max-w-2xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-[#1B3A8A]">Upload Center</h1>
        <p className="text-gray-500 text-sm mt-1">
          Upload your billing Excel sheet and PDF ZIP to begin processing.
        </p>
      </div>

      {uploadError && (
        <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-700">{uploadError}</p>
        </div>
      )}

      <div className="space-y-4 mb-8">
        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
            Step 1 — Billing Excel Sheet
          </label>
          <ExcelDropzone file={excelFile} onFile={setExcelFile} disabled={isPending} />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
            Step 2 — PDF Reports ZIP
          </label>
          <ZipDropzone file={zipFile} onFile={setZipFile} disabled={isPending} />
        </div>
      </div>

      <button
        className="btn-primary w-full justify-center"
        disabled={!canSubmit}
        onClick={handleSubmit}
      >
        {isPending ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Processing files...
          </>
        ) : (
          <>
            Parse & Validate
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>

      <div className="mt-8 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">
          Required Excel Columns
        </p>
        <div className="grid grid-cols-2 gap-1 text-xs text-gray-500">
          {[
            'COMPANY NAME', 'Email', 'Ticket Number', 'NOTES',
            'CC', 'BCC', 'Rate', 'Currency',
            'Total', 'Converted USD', 'Total to Charge', 'Past Due',
          ].map((col) => (
            <span key={col} className="font-mono">• {col}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

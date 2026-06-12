import { useNavigate } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';
import { ErrorLog } from '../components/logs/ErrorLog';
import { useUploadStore } from '../store/uploadStore';

export function LogsPage() {
  const navigate = useNavigate();
  const { uploadResponse } = useUploadStore();

  if (!uploadResponse) {
    return (
      <div className="p-8 flex flex-col items-center justify-center min-h-[60vh] text-center">
        <AlertCircle className="w-10 h-10 text-gray-300 mb-3" />
        <p className="text-sm text-gray-500">No session active.</p>
        <button className="btn-primary mt-4" onClick={() => navigate('/')}>
          Upload Files
        </button>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#1B3A8A]">Error Logs</h1>
        <p className="text-gray-500 text-sm mt-1">
          All validation failures and send errors from current session.
        </p>
      </div>
      <ErrorLog rows={uploadResponse.rows} />
    </div>
  );
}

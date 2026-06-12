import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { ExportRecord } from '../types';
import { useUploadStore } from '../store/uploadStore';

export function useExportList() {
  const { sessionId } = useUploadStore();

  return useQuery({
    queryKey: ['exports', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const res = await api.get<{ records: ExportRecord[] }>(`/export?sessionId=${sessionId}`);
      return res.data.records;
    },
    enabled: !!sessionId,
  });
}

export function downloadFile(filename: string): void {
  const link = document.createElement('a');
  link.href = `/api/export/${encodeURIComponent(filename)}`;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

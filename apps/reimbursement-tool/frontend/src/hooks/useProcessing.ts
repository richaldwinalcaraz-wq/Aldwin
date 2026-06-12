import { useEffect, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useUploadStore } from '../store/uploadStore';
import { useProcessingStore } from '../store/processingStore';
import { SSEEvent } from '../types';

export function useApproveSend() {
  const { sessionId } = useUploadStore();
  const { startProcessing, updateRowStatus, setProgress, setComplete } = useProcessingStore();

  const approveMutation = useMutation({
    mutationFn: async (params: { rowIndexes?: number[]; approveAll?: boolean }) => {
      await api.post('/process/approve', { sessionId, ...params });
    },
  });

  const sendMutation = useMutation({
    mutationFn: async () => {
      startProcessing();
      await api.post('/process/send', { sessionId });
    },
  });

  // Wire SSE when processing starts
  const sseRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!sendMutation.isPending || !sessionId) return;

    const es = new EventSource(`/api/process/status?sessionId=${sessionId}`);
    sseRef.current = es;

    es.onmessage = (e) => {
      try {
        const event: SSEEvent = JSON.parse(e.data);

        if (event.type === 'row_update' && event.rowIndex !== undefined) {
          updateRowStatus({
            rowIndex: event.rowIndex,
            sendStatus: event.status ?? 'PENDING',
            message: event.message ?? '',
            ticketId: event.ticketId,
          });
          if (event.current !== undefined && event.total !== undefined) {
            setProgress(event.current, event.total);
          }
        }

        if (event.type === 'complete') {
          setComplete(event.exportFilename);
          es.close();
        }

        if (event.type === 'progress' && event.current !== undefined && event.total !== undefined) {
          setProgress(event.current, event.total);
        }
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      es.close();
    };

    return () => {
      es.close();
    };
  }, [sendMutation.isPending, sessionId]);

  return { approveMutation, sendMutation };
}

export function useExportGenerate() {
  const { sessionId } = useUploadStore();
  const { setExportRecords } = useProcessingStore();

  return useMutation({
    mutationFn: async () => {
      const res = await api.post<{ filename: string; totalSent: number; failedRows: number }>(
        '/export',
        { sessionId }
      );
      return res.data;
    },
    onSuccess: async () => {
      const res = await api.get<{ records: { filename: string; processedDate: string; totalSent: number; failedRows: number }[] }>(
        `/export?sessionId=${sessionId}`
      );
      setExportRecords(res.data.records);
    },
  });
}

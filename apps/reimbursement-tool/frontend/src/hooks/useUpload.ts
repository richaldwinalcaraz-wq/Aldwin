import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useUploadStore } from '../store/uploadStore';
import { UploadResponse } from '../types';

export function useUpload() {
  const { setUploading, setUploadResponse, setUploadError } = useUploadStore();

  return useMutation({
    mutationFn: async (formData: FormData): Promise<UploadResponse> => {
      setUploading(true);
      const res = await api.post<UploadResponse>('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,
      });
      return res.data;
    },
    onSuccess: (data) => {
      setUploadResponse(data);
    },
    onError: (err: Error) => {
      setUploadError(err.message);
    },
    onSettled: () => {
      setUploading(false);
    },
  });
}

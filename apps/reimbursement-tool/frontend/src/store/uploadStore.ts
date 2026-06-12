import { create } from 'zustand';
import { ProcessedRow, UploadResponse } from '../types';

interface UploadState {
  sessionId: string | null;
  uploadResponse: UploadResponse | null;
  isUploading: boolean;
  uploadError: string | null;
  setUploading: (v: boolean) => void;
  setUploadResponse: (data: UploadResponse) => void;
  setUploadError: (err: string | null) => void;
  updateRow: (rowIndex: number, update: Partial<ProcessedRow>) => void;
  reset: () => void;
}

export const useUploadStore = create<UploadState>((set) => ({
  sessionId: null,
  uploadResponse: null,
  isUploading: false,
  uploadError: null,

  setUploading: (v) => set({ isUploading: v }),

  setUploadResponse: (data) =>
    set({ uploadResponse: data, sessionId: data.sessionId, uploadError: null }),

  setUploadError: (err) => set({ uploadError: err, isUploading: false }),

  updateRow: (rowIndex, update) =>
    set((state) => {
      if (!state.uploadResponse) return state;
      const rows = state.uploadResponse.rows.map((r) =>
        r.rowIndex === rowIndex ? { ...r, ...update } : r
      );
      return { uploadResponse: { ...state.uploadResponse, rows } };
    }),

  reset: () =>
    set({
      sessionId: null,
      uploadResponse: null,
      isUploading: false,
      uploadError: null,
    }),
}));

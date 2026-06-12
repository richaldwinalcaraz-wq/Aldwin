import { create } from 'zustand';
import { SendStatus } from '../types';
import { ExportRecord } from '../types';

interface RowStatus {
  rowIndex: number;
  sendStatus: SendStatus;
  message: string;
  ticketId?: string;
  dateSent?: string;
}

interface ProcessingState {
  isProcessing: boolean;
  progress: { current: number; total: number };
  rowStatuses: Map<number, RowStatus>;
  exportFilename: string | null;
  exportRecords: ExportRecord[];
  lastMessage: string;

  startProcessing: () => void;
  updateRowStatus: (status: RowStatus) => void;
  setProgress: (current: number, total: number) => void;
  setComplete: (exportFilename?: string) => void;
  setExportRecords: (records: ExportRecord[]) => void;
  reset: () => void;
}

export const useProcessingStore = create<ProcessingState>((set) => ({
  isProcessing: false,
  progress: { current: 0, total: 0 },
  rowStatuses: new Map(),
  exportFilename: null,
  exportRecords: [],
  lastMessage: '',

  startProcessing: () =>
    set({ isProcessing: true, exportFilename: null, rowStatuses: new Map() }),

  updateRowStatus: (status) =>
    set((state) => {
      const next = new Map(state.rowStatuses);
      next.set(status.rowIndex, status);
      return { rowStatuses: next, lastMessage: status.message };
    }),

  setProgress: (current, total) =>
    set({ progress: { current, total } }),

  setComplete: (exportFilename) =>
    set({ isProcessing: false, exportFilename: exportFilename ?? null }),

  setExportRecords: (records) => set({ exportRecords: records }),

  reset: () =>
    set({
      isProcessing: false,
      progress: { current: 0, total: 0 },
      rowStatuses: new Map(),
      exportFilename: null,
      lastMessage: '',
    }),
}));

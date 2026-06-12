import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { HubSpotTemplateIds } from '../types';

interface SettingsState {
  hubspotToken: string;
  processedBy: string;
  templateIds: HubSpotTemplateIds;
  isSaving: boolean;
  lastSaved: string | null;

  setHubspotToken: (token: string) => void;
  setProcessedBy: (name: string) => void;
  setTemplateIds: (ids: Partial<HubSpotTemplateIds>) => void;
  setIsSaving: (v: boolean) => void;
  setLastSaved: (ts: string) => void;
}

const defaultTemplateIds: HubSpotTemplateIds = {
  standard: '',
  informational: '',
  follow_up: '',
  resubmission: '',
  priority: '',
  fromEmail: '',
};

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      hubspotToken: '',
      processedBy: '',
      templateIds: defaultTemplateIds,
      isSaving: false,
      lastSaved: null,

      setHubspotToken: (token) => set({ hubspotToken: token }),
      setProcessedBy: (name) => set({ processedBy: name }),
      setTemplateIds: (partial) =>
        set((state) => ({ templateIds: { ...state.templateIds, ...partial } })),
      setIsSaving: (v) => set({ isSaving: v }),
      setLastSaved: (ts) => set({ lastSaved: ts }),
    }),
    {
      name: 'reimbursement-settings',
      partialize: (state) => ({
        processedBy: state.processedBy,
        templateIds: state.templateIds,
      }),
    }
  )
);

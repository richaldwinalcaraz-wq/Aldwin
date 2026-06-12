import { HubSpotSettings } from '../components/settings/HubSpotSettings';

export function SettingsPage() {
  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-[#1B3A8A]">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">
          Configure HubSpot API and email delivery.
        </p>
      </div>
      <HubSpotSettings />
    </div>
  );
}

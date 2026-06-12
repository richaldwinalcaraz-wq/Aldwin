import { NavLink } from 'react-router-dom';
import {
  Upload,
  LayoutDashboard,
  Mail,
  Settings,
  Download,
  AlertCircle,
} from 'lucide-react';
import { useUploadStore } from '../../store/uploadStore';

const NAV_ITEMS = [
  { path: '/', label: 'Upload Center', icon: Upload },
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/downloads', label: 'Downloads', icon: Download },
  { path: '/templates', label: 'Templates', icon: Mail },
  { path: '/logs', label: 'Error Logs', icon: AlertCircle },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar() {
  const { uploadResponse } = useUploadStore();

  return (
    <aside className="w-56 min-h-screen bg-[#1B3A8A] flex flex-col">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-white/10">
        <img
          src="/riverbend-logo.png"
          alt="Riverbend Consulting"
          className="w-40 object-contain"
        />
        <p className="text-[10px] text-white/50 mt-2 tracking-wide">Reimbursement Sender</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 px-3 space-y-0.5">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? 'bg-[#F47920] text-white font-medium'
                  : 'text-white/70 hover:text-white hover:bg-white/10'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Session status */}
      {uploadResponse && (
        <div className="px-4 py-4 border-t border-white/10 bg-[#152e6e]">
          <p className="text-[10px] text-white/40 uppercase tracking-wider mb-2">
            Active Session
          </p>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-white/60">Total rows</span>
              <span className="text-white font-medium">{uploadResponse.totalRows}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-white/60">Ready</span>
              <span className="text-green-300">{uploadResponse.validRows}</span>
            </div>
            {uploadResponse.missingPdfs > 0 && (
              <div className="flex justify-between text-xs">
                <span className="text-white/60">Missing PDFs</span>
                <span className="text-red-300">{uploadResponse.missingPdfs}</span>
              </div>
            )}
            {uploadResponse.noAccessRows > 0 && (
              <div className="flex justify-between text-xs">
                <span className="text-white/60">No Access</span>
                <span className="text-amber-300">{uploadResponse.noAccessRows}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}

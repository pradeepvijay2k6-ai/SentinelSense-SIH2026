import React from 'react';
import { Stethoscope, ShieldAlert } from 'lucide-react';
import type { RoleView } from '../types';

interface RoleToggleProps {
  currentRole: RoleView;
  onRoleChange: (role: RoleView) => void;
}

export const RoleToggle: React.FC<RoleToggleProps> = ({ currentRole, onRoleChange }) => {
  return (
    <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-800 shadow-inner">
      <button
        onClick={() => onRoleChange('COMMANDER')}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
          currentRole === 'COMMANDER'
            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        title="Commander View: Tactical readiness verdicts, fatigue risk bands, no raw biosignal waveforms"
      >
        <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
        <span>Commander View</span>
      </button>

      <button
        onClick={() => onRoleChange('MEDICAL_OFFICER')}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
          currentRole === 'MEDICAL_OFFICER'
            ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
            : 'text-slate-400 hover:text-slate-200'
        }`}
        title="Medical Officer View: Full clinical detail, raw/filtered waveforms, HRV spectra, oximetry curves"
      >
        <Stethoscope className="w-3.5 h-3.5 text-cyan-400" />
        <span>Medical Officer View</span>
      </button>
    </div>
  );
};

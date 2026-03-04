import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui';
import { ROLE_HOME_ROUTES, ROLE_LABELS } from '@/constants';
import type { UserRole } from '@/types';
import { Shield, User, Heart, ClipboardList, BarChart3, Settings } from 'lucide-react';

const roleIcons: Record<UserRole, typeof User> = {
  psw: Heart,
  nurse: User,
  supervisor: ClipboardList,
  executive: BarChart3,
  admin: Settings,
};

const roleDescriptions: Record<UserRole, string> = {
  psw: 'Mobile-first alerts, room grid, one-tap acknowledge',
  nurse: 'Alerts, shift summary, reports, incident exports',
  supervisor: 'Review queue, triage, clip access, full oversight',
  executive: 'Trends, KPIs, board-ready reporting',
  admin: 'System health, facility, storage, settings',
};

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (role: UserRole) => {
    await login(role);
    navigate(ROLE_HOME_ROUTES[role]);
  };

  return (
    <div className="w-full max-w-md">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center gap-2 mb-3">
          <Shield className="h-10 w-10 text-elder-action" />
          <h1 className="text-2xl font-bold text-elder-text-primary">ElderOS Vision</h1>
        </div>
        <p className="text-sm text-elder-text-secondary">Room Safety Monitoring System</p>
      </div>

      <div className="bg-elder-surface rounded-xl shadow-lg border border-elder-border p-6 space-y-3">
        
        {(Object.keys(ROLE_LABELS) as UserRole[]).map(role => {
          const Icon = roleIcons[role];
          return (
            <button
              key={role}
              onClick={() => handleLogin(role)}
              className="w-full flex items-center gap-4 p-4 rounded-lg border border-elder-border hover:border-elder-action hover:bg-elder-action-bg transition-colors text-left group"
            >
              <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-elder-action-bg text-elder-action group-hover:bg-elder-action group-hover:text-white transition-colors">
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-elder-text-primary">{ROLE_LABELS[role]}</p>
                <p className="text-xs text-elder-text-secondary">{roleDescriptions[role]}</p>
              </div>
            </button>
          );
        })}
      </div>

      <p className="text-xs text-elder-text-muted text-center mt-4">
        Stand-alone on-prem system — no external connectivity required
      </p>
    </div>
  );
}

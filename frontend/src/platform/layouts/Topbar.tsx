import { useState } from 'react';
import { Bell, LogOut, Menu } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAlerts } from '@/hooks/useAlerts';
import { useInterval } from '@/hooks/useInterval';
import { cn } from '@/utils/cn';
import { ROLE_LABELS } from '@/constants';
import { Badge } from '@/components/ui';

interface TopbarProps {
  onMenuToggle?: () => void;
  showMenu?: boolean;
}

export function Topbar({ onMenuToggle, showMenu }: TopbarProps) {
  const { user, logout } = useAuth();
  const { unacknowledgedCount } = useAlerts();
  const [clock, setClock] = useState(formatClock());

  useInterval(() => setClock(formatClock()), 1000);

  if (!user) return null;

  return (
    <header className="h-topbar-h bg-elder-surface border-b border-elder-border flex items-center justify-between px-4 sticky top-0 z-30">
      <div className="flex items-center gap-3">
        {showMenu && (
          <button onClick={onMenuToggle} className="text-elder-text-secondary hover:text-elder-text-primary lg:hidden" aria-label="Toggle menu">
            <Menu className="h-5 w-5" />
          </button>
        )}
        <span className="font-semibold text-sm text-elder-action hidden sm:block">ElderOS Vision</span>
      </div>

      <div className="font-mono text-sm text-elder-text-secondary tabular-nums">{clock}</div>

      <div className="flex items-center gap-3">
        <div className="relative">
          <Bell className="h-5 w-5 text-elder-text-secondary" />
          {unacknowledgedCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-elder-critical text-[10px] font-bold text-white px-1">
              {unacknowledgedCount}
            </span>
          )}
        </div>
        <Badge variant="info">{ROLE_LABELS[user.role]}</Badge>
        <div className="flex items-center justify-center h-7 w-7 rounded-full bg-elder-action text-white text-xs font-medium">
          {user.avatarInitials}
        </div>
        <button onClick={logout} className="text-elder-text-muted hover:text-elder-text-primary" aria-label="Logout" title="Logout">
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}

function formatClock(): string {
  const now = new Date();
  return now.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

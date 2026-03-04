import { AlertTriangle, Bell } from 'lucide-react';
import { cn } from '@/utils/cn';

interface AlertBannerProps {
  count: number;
  criticalCount: number;
  onClick?: () => void;
}

export function AlertBanner({ count, criticalCount, onClick }: AlertBannerProps) {
  if (count === 0) return null;

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg text-sm font-semibold text-white',
        criticalCount > 0 ? 'bg-elder-critical animate-pulse-critical' : 'bg-elder-warning'
      )}
    >
      {criticalCount > 0 ? <AlertTriangle className="h-4 w-4" /> : <Bell className="h-4 w-4" />}
      {count} unacknowledged alert{count !== 1 ? 's' : ''}
      {criticalCount > 0 && ` (${criticalCount} critical)`}
    </button>
  );
}

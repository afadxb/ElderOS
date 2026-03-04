import { StatusDot } from '@/components/ui';
import type { SystemMetrics } from '@/types';

interface NTPDriftIndicatorProps {
  metrics: SystemMetrics;
}

const statusMap = {
  synced: { color: 'green' as const, label: 'Synchronized' },
  drifting: { color: 'yellow' as const, label: 'Drifting' },
  lost: { color: 'red' as const, label: 'Sync Lost' },
};

export function NTPDriftIndicator({ metrics }: NTPDriftIndicatorProps) {
  const status = statusMap[metrics.ntpSyncStatus];

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-2">
        <StatusDot color={status.color} pulse={metrics.ntpSyncStatus === 'lost'} />
        <span className="text-sm font-medium">{status.label}</span>
      </div>
      <span className="text-sm font-mono text-elder-text-secondary">{metrics.ntpDriftMs}ms drift</span>
    </div>
  );
}

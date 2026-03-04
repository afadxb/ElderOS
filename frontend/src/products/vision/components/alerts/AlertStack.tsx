import type { AlertEvent } from '@/types';
import { AlertCard } from './AlertCard';
import { EmptyState } from '@/components/ui';
import { Bell } from 'lucide-react';

interface AlertStackProps {
  alerts: AlertEvent[];
  onAcknowledge: (eventId: string) => void;
  onResolve: (eventId: string) => void;
}

export function AlertStack({ alerts, onAcknowledge, onResolve }: AlertStackProps) {
  if (alerts.length === 0) {
    return <EmptyState icon={<Bell className="h-12 w-12" />} title="No active alerts" description="All clear — no unresolved alerts at this time." />;
  }

  return (
    <div className="space-y-2">
      {alerts.map(alert => (
        <AlertCard
          key={alert.id}
          event={alert}
          onAcknowledge={onAcknowledge}
          onResolve={onResolve}
          compact
        />
      ))}
    </div>
  );
}

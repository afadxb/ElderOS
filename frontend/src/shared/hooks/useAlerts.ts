import { useCallback, useMemo } from 'react';
import { useAlertStore } from '@/platform/stores/alertStore';
import { useAuth } from '@/shared/hooks/useAuth';
import { mockStore } from '@/mock';

export function useAlerts() {
  const { user } = useAuth();
  const activeAlerts = useAlertStore((s) => s.activeAlerts);
  const recentEvents = useAlertStore((s) => s.recentEvents);
  const unacknowledgedCount = useAlertStore((s) => s.unacknowledgedCount);
  const storeAcknowledge = useAlertStore((s) => s.acknowledge);
  const storeResolve = useAlertStore((s) => s.resolve);

  // Derive filtered lists via useMemo — avoids Zustand infinite re-render
  // (selector-based .filter() returns new array ref every call)
  const criticalAlerts = useMemo(
    () => activeAlerts.filter((a) => a.severity === 'critical'),
    [activeAlerts]
  );
  const warningAlerts = useMemo(
    () => activeAlerts.filter((a) => a.severity === 'warning'),
    [activeAlerts]
  );

  const acknowledge = useCallback(
    (eventId: string) => {
      if (!user) return;
      mockStore.acknowledgeEvent(eventId, user.id);
      storeAcknowledge(eventId, user.id);
    },
    [user, storeAcknowledge]
  );

  const resolve = useCallback(
    (eventId: string) => {
      if (!user) return;
      mockStore.resolveEvent(eventId, user.id);
      storeResolve(eventId, user.id);
    },
    [user, storeResolve]
  );

  return {
    activeAlerts,
    recentEvents,
    unacknowledgedCount,
    acknowledge,
    resolve,
    criticalAlerts,
    warningAlerts,
    hasCritical: criticalAlerts.length > 0,
  };
}

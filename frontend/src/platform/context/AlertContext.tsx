import { createContext, useEffect, useRef, type ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAlertStore } from '@/platform/stores/alertStore';
import { mockStore } from '@/mock';
import { connectAlertStream } from '@/platform/services/websocketService';
import { useAuth } from '@/hooks/useAuth';

// Context kept for provider wrapper — state now lives in Zustand store
export const AlertContext = createContext<null>(null);

export function AlertProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const disconnectRef = useRef<(() => void) | null>(null);
  const setAlerts = useAlertStore((s) => s.setAlerts);
  const addAlert = useAlertStore((s) => s.addAlert);

  useEffect(() => {
    if (!isAuthenticated) return;

    // Seed store from mock data
    const active = mockStore.getActiveAlerts();
    const cutoff = new Date(Date.now() - 60 * 60 * 1000);
    const recent = mockStore.events.filter(e => new Date(e.detectedAt) >= cutoff).slice(0, 100);
    setAlerts(active, recent);

    // Connect simulated WebSocket
    const { disconnect } = connectAlertStream({
      onAlert: (alert) => {
        mockStore.addEvent(alert);
        addAlert(alert);
      },
      onSystemUpdate: () => {
        const active = mockStore.getActiveAlerts();
        const cutoff = new Date(Date.now() - 60 * 60 * 1000);
        const recent = mockStore.events.filter(e => new Date(e.detectedAt) >= cutoff).slice(0, 100);
        setAlerts(active, recent);
      },
      onDataChange: (queryKeys) => {
        // Invalidate TanStack Query caches when server signals data changes
        for (const key of queryKeys) {
          queryClient.invalidateQueries({ queryKey: key });
        }
      },
    });
    disconnectRef.current = disconnect;

    return () => {
      disconnect();
      disconnectRef.current = null;
    };
  }, [isAuthenticated, setAlerts, addAlert, queryClient]);

  return (
    <AlertContext.Provider value={null}>
      {children}
    </AlertContext.Provider>
  );
}

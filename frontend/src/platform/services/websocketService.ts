import type { AlertEvent } from '@/types';
import { generateNextAlert } from '@/mock/generators/alerts';

interface AlertStreamCallbacks {
  onAlert: (alert: AlertEvent) => void;
  onSystemUpdate?: () => void;
  onDataChange?: (queryKeys: string[][]) => void;
}

interface AlertStreamConnection {
  disconnect: () => void;
  isConnected: () => boolean;
}

/**
 * Connect to the alert stream.
 *
 * In production this will be a real WebSocket via reconnecting-websocket.
 * For now it simulates the same event contract with setInterval so the
 * rest of the stack (Zustand stores, TanStack Query invalidation) is
 * already wired correctly.
 *
 * Event contract:
 *   - alert events      → Zustand alertStore (immediate UI update)
 *   - system heartbeats  → onSystemUpdate callback → Zustand systemStore
 *   - data change signals → onDataChange callback  → queryClient.invalidateQueries
 */
export function connectAlertStream(callbacks: AlertStreamCallbacks): AlertStreamConnection {
  let connected = true;

  // Simulate WebSocket — inject new alert every 20-40 seconds
  const alertInterval = setInterval(() => {
    if (!connected) return;
    const alert = generateNextAlert();
    if (alert) {
      callbacks.onAlert(alert);
    }
  }, 20000 + Math.random() * 20000);

  // System health update every 60 seconds
  const sysInterval = setInterval(() => {
    if (!connected) return;
    callbacks.onSystemUpdate?.();
  }, 60000);

  // Simulate data change notification every 90 seconds
  // (in production, the server pushes these when room/resident data changes)
  const dataInterval = setInterval(() => {
    if (!connected) return;
    callbacks.onDataChange?.([['rooms'], ['residents']]);
  }, 90000);

  return {
    disconnect: () => {
      connected = false;
      clearInterval(alertInterval);
      clearInterval(sysInterval);
      clearInterval(dataInterval);
    },
    isConnected: () => connected,
  };
}

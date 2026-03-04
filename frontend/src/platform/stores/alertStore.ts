import { create } from 'zustand';
import type { AlertEvent } from '@/types';

interface AlertState {
  activeAlerts: AlertEvent[];
  recentEvents: AlertEvent[];
  unacknowledgedCount: number;
}

interface AlertActions {
  addAlert: (alert: AlertEvent) => void;
  acknowledge: (eventId: string, userId: string) => void;
  resolve: (eventId: string, userId: string) => void;
  setAlerts: (active: AlertEvent[], recent: AlertEvent[]) => void;
  refresh: (getActive: () => AlertEvent[], getRecent: () => AlertEvent[]) => void;
}

export type AlertStore = AlertState & AlertActions;

export const useAlertStore = create<AlertStore>((set) => ({
  activeAlerts: [],
  recentEvents: [],
  unacknowledgedCount: 0,

  addAlert: (alert) =>
    set((state) => ({
      activeAlerts: [alert, ...state.activeAlerts],
      recentEvents: [alert, ...state.recentEvents].slice(0, 100),
      unacknowledgedCount: state.unacknowledgedCount + 1,
    })),

  acknowledge: (eventId, userId) =>
    set((state) => {
      const updated = state.activeAlerts.map((a) =>
        a.id === eventId
          ? { ...a, status: 'acknowledged' as const, acknowledgedAt: new Date().toISOString(), acknowledgedBy: userId }
          : a
      );
      return {
        activeAlerts: updated,
        unacknowledgedCount: updated.filter((a) => a.status === 'active').length,
      };
    }),

  resolve: (eventId, userId) =>
    set((state) => {
      const resolvedEvent = state.activeAlerts.find((a) => a.id === eventId);
      const remaining = state.activeAlerts.filter((a) => a.id !== eventId);
      const updatedRecent = resolvedEvent
        ? state.recentEvents.map((e) =>
            e.id === eventId
              ? { ...e, status: 'resolved' as const, resolvedAt: new Date().toISOString(), resolvedBy: userId }
              : e
          )
        : state.recentEvents;
      return {
        activeAlerts: remaining,
        recentEvents: updatedRecent,
        unacknowledgedCount: remaining.filter((a) => a.status === 'active').length,
      };
    }),

  setAlerts: (active, recent) =>
    set({
      activeAlerts: active,
      recentEvents: recent,
      unacknowledgedCount: active.filter((a) => a.status === 'active').length,
    }),

  refresh: (getActive, getRecent) =>
    set({
      activeAlerts: getActive(),
      recentEvents: getRecent(),
      unacknowledgedCount: getActive().filter((a) => a.status === 'active').length,
    }),
}));

// Selectors
export const selectCriticalAlerts = (state: AlertStore) =>
  state.activeAlerts.filter((a) => a.severity === 'critical');

export const selectWarningAlerts = (state: AlertStore) =>
  state.activeAlerts.filter((a) => a.severity === 'warning');

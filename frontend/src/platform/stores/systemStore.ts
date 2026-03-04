import { create } from 'zustand';
import type { SystemMetrics, SensorHealth } from '@/types';

interface SystemState {
  metrics: SystemMetrics | null;
  sensors: SensorHealth[];
  lastUpdated: string | null;
}

interface SystemActions {
  setMetrics: (metrics: SystemMetrics) => void;
  setSensors: (sensors: SensorHealth[]) => void;
  updateSensorStatus: (sensorId: string, online: boolean) => void;
}

export type SystemStore = SystemState & SystemActions;

export const useSystemStore = create<SystemStore>((set) => ({
  metrics: null,
  sensors: [],
  lastUpdated: null,

  setMetrics: (metrics) =>
    set({ metrics, lastUpdated: new Date().toISOString() }),

  setSensors: (sensors) =>
    set({ sensors, lastUpdated: new Date().toISOString() }),

  updateSensorStatus: (sensorId, online) =>
    set((state) => ({
      sensors: state.sensors.map((s) =>
        s.sensorId === sensorId
          ? { ...s, status: online ? ('online' as const) : ('offline' as const), online }
          : s
      ),
      lastUpdated: new Date().toISOString(),
    })),
}));

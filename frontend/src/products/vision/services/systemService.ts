import type { SensorHealth, SystemMetrics } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

export async function getCameraHealth(): Promise<SensorHealth[]> {
  await simulateLatency();
  return mockStore.sensors;
}

export async function getSystemMetrics(): Promise<SystemMetrics> {
  await simulateLatency();
  return mockStore.systemMetrics;
}

export async function getSelfTestReport(): Promise<{ passed: boolean; details: string[] }> {
  await simulateLatency();
  const sensorCount = mockStore.sensors.length;
  return {
    passed: mockStore.systemMetrics.selfTestPassed,
    details: [
      `Sensor connectivity: All ${sensorCount} sensors responding`,
      'Inference pipeline: Latency within baseline',
      `Storage: ${mockStore.systemMetrics.diskUsedGB} GB / ${mockStore.systemMetrics.diskTotalGB} GB used (${mockStore.systemMetrics.diskUsagePercent}%)`,
      'NTP synchronization: Drift < 5ms',
      'Database integrity: All tables verified',
      mockStore.systemMetrics.selfTestPassed
        ? 'Overall: PASS'
        : 'WARNING: 2 sensors showing degraded performance',
    ],
  };
}

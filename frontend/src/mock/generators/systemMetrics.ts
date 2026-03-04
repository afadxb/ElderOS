import type { SystemMetrics } from '@/types';
import { randomInt, randomFloat } from '../helpers';

export function generateSystemMetrics(): SystemMetrics {
  const ntpDrift = randomInt(0, 50);
  return {
    cpuUsage: randomFloat(20, 60),
    memoryUsage: randomFloat(40, 70),
    diskUsagePercent: randomFloat(30, 80),
    diskUsedGB: randomFloat(300, 800),
    diskTotalGB: 1000,
    retentionDays: 7,
    autoPurgeThresholdPercent: 90,
    ntpDriftMs: ntpDrift,
    ntpSyncStatus: ntpDrift < 10 ? 'synced' : ntpDrift < 30 ? 'drifting' : 'lost',
    lastSelfTestAt: new Date().toISOString(),
    selfTestPassed: randomInt(1, 100) <= 95,
    edgeDeviceUptime: `${randomInt(1, 30)}d ${randomInt(0, 23)}h ${randomInt(0, 59)}m`,
  };
}

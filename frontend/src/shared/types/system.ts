export type SensorHealthStatus = 'online' | 'degraded' | 'offline';

/** @deprecated Use SensorHealthStatus instead */
export type CameraStatus = SensorHealthStatus;

export interface SensorHealth {
  sensorId: string;
  type: 'ai-vision' | 'ai-sensor';
  roomId: string;
  roomNumber: string;
  status: SensorHealthStatus;
  lastHeartbeat: string;
  inferenceLatencyMs: number;
  baselineLatencyMs: number;
  uptime: number;
  firmwareVersion: string;
}

/** @deprecated Use SensorHealth instead */
export type CameraHealth = SensorHealth;

export interface SystemMetrics {
  cpuUsage: number;
  memoryUsage: number;
  diskUsagePercent: number;
  diskUsedGB: number;
  diskTotalGB: number;
  retentionDays: number;
  autoPurgeThresholdPercent: number;
  ntpDriftMs: number;
  ntpSyncStatus: 'synced' | 'drifting' | 'lost';
  lastSelfTestAt: string;
  selfTestPassed: boolean;
  edgeDeviceUptime: string;
}

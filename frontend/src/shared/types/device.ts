export type DeviceType = 'ai-vision' | 'ai-sensor';
export type DeviceStatus = 'online' | 'degraded' | 'offline';

export interface DeviceConnectionConfig {
  rtspUrl?: string;
  serialPort?: string;
  baudRate?: number;
}

export interface DeviceDetectionConfig {
  sensitivity?: number;
  bedZoneEnabled?: boolean;
  [key: string]: unknown;
}

export interface Device {
  id: string;
  roomId: string;
  roomNumber: string | null;
  type: DeviceType | null;
  name: string | null;
  status: DeviceStatus;
  enabled: boolean;
  edgeDeviceId: string | null;
  lastHeartbeat: string | null;
  inferenceLatencyMs: number;
  baselineLatencyMs: number;
  uptime: number;
  firmwareVersion: string;
  connectionConfig: DeviceConnectionConfig | null;
  detectionConfig: DeviceDetectionConfig | null;
}

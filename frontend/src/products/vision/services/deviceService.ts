import type { Device, DeviceType } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';
import { uuid } from '@/mock/helpers';

export async function getDevices(filters?: {
  roomId?: string;
  type?: DeviceType;
}): Promise<Device[]> {
  await simulateLatency();
  let devices = mockStore.devices;
  if (filters?.roomId) {
    devices = devices.filter(d => d.roomId === filters.roomId);
  }
  if (filters?.type) {
    devices = devices.filter(d => d.type === filters.type);
  }
  return devices;
}

export async function getDevice(id: string): Promise<Device | undefined> {
  await simulateLatency();
  return mockStore.devices.find(d => d.id === id);
}

export async function addDevice(data: {
  roomId: string;
  roomNumber: string;
  type: DeviceType;
  name: string;
  edgeDeviceId: string;
  enabled: boolean;
  connectionConfig: Device['connectionConfig'];
}): Promise<Device> {
  await simulateLatency();
  const device: Device = {
    id: uuid(),
    roomId: data.roomId,
    roomNumber: data.roomNumber,
    type: data.type,
    name: data.name,
    status: 'offline',
    enabled: data.enabled,
    edgeDeviceId: data.edgeDeviceId,
    lastHeartbeat: null,
    inferenceLatencyMs: 0,
    baselineLatencyMs: data.type === 'ai-vision' ? 80 : 15,
    uptime: 0,
    firmwareVersion: data.type === 'ai-vision' ? 'v2.0.0' : 'r1.0.0',
    connectionConfig: data.connectionConfig,
    detectionConfig: null,
  };
  mockStore.addDevice(device);
  return device;
}

export async function updateDevice(
  id: string,
  updates: Partial<Pick<Device, 'roomId' | 'roomNumber' | 'type' | 'name' | 'edgeDeviceId' | 'enabled' | 'connectionConfig'>>,
): Promise<void> {
  await simulateLatency();
  mockStore.updateDevice(id, updates);
}

export async function removeDevice(id: string): Promise<void> {
  await simulateLatency();
  mockStore.removeDevice(id);
}

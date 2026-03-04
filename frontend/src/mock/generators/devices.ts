import type { Device, DeviceStatus } from '@/types';
import type { Room } from '@/types';
import { uuid, randomInt, randomFloat, randomPick } from '../helpers';

const EDGE_DEVICE_IDS = ['edge-floor1', 'edge-floor2', 'edge-floor3'];

export function generateDevices(rooms: Room[]): Device[] {
  const devices: Device[] = [];

  for (const room of rooms) {
    for (const sensor of room.sensors) {
      const roll = randomInt(1, 100);
      let status: DeviceStatus;
      let latency: number;

      if (roll <= 88) {
        status = 'online';
        latency = sensor.type === 'ai-sensor' ? randomInt(5, 30) : randomInt(40, 150);
      } else if (roll <= 95) {
        status = 'degraded';
        latency = sensor.type === 'ai-sensor' ? randomInt(50, 100) : randomInt(200, 500);
      } else {
        status = 'offline';
        latency = 0;
      }

      const now = new Date();
      const lastHeartbeat = status === 'offline'
        ? new Date(now.getTime() - randomInt(300, 3600) * 1000)
        : new Date(now.getTime() - randomInt(5, 55) * 1000);

      const isVision = sensor.type === 'ai-vision';

      devices.push({
        id: sensor.id,
        roomId: room.id,
        roomNumber: room.number,
        type: sensor.type as Device['type'],
        name: isVision
          ? `Camera ${room.number}`
          : `Radar ${room.number}`,
        status,
        enabled: randomInt(1, 100) <= 95,
        edgeDeviceId: randomPick(EDGE_DEVICE_IDS),
        lastHeartbeat: lastHeartbeat.toISOString(),
        inferenceLatencyMs: latency,
        baselineLatencyMs: isVision ? 80 : 15,
        uptime: status === 'offline' ? randomFloat(85, 95) : randomFloat(97, 99.99),
        firmwareVersion: isVision
          ? `v2.${randomInt(1, 4)}.${randomInt(0, 12)}`
          : `r1.${randomInt(0, 3)}.${randomInt(0, 8)}`,
        connectionConfig: isVision
          ? { rtspUrl: `rtsp://192.168.1.${randomInt(10, 250)}:554/stream${randomInt(1, 4)}` }
          : { serialPort: `/dev/ttyUSB${randomInt(0, 3)}`, baudRate: 115200 },
        detectionConfig: { sensitivity: randomInt(60, 95), bedZoneEnabled: true },
      });
    }
  }

  return devices;
}

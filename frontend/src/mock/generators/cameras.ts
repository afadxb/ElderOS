import type { SensorHealth, SensorHealthStatus } from '@/types';
import type { Room } from '@/types';
import { randomInt, randomFloat } from '../helpers';

export function generateCameraHealth(rooms: Room[]): SensorHealth[] {
  const sensorHealthRecords: SensorHealth[] = [];

  for (const room of rooms) {
    for (const sensor of room.sensors) {
      const roll = randomInt(1, 100);
      let status: SensorHealthStatus;
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

      sensorHealthRecords.push({
        sensorId: sensor.id,
        type: sensor.type,
        roomId: room.id,
        roomNumber: room.number,
        status,
        lastHeartbeat: lastHeartbeat.toISOString(),
        inferenceLatencyMs: latency,
        baselineLatencyMs: sensor.type === 'ai-sensor' ? 15 : 80,
        uptime: status === 'offline' ? randomFloat(85, 95) : randomFloat(97, 99.99),
        firmwareVersion: sensor.type === 'ai-sensor'
          ? `r1.${randomInt(0, 3)}.${randomInt(0, 8)}`
          : `v2.${randomInt(1, 4)}.${randomInt(0, 12)}`,
      });
    }
  }

  return sensorHealthRecords;
}

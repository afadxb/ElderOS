import type { Room, SensorType, RoomType } from '@/types';
import { uuid, randomInt, randomPick } from '../helpers';

export function generateRooms(): Room[] {
  const rooms: Room[] = [];
  const units = [
    { name: 'Unit A', floor: 1, prefix: '1' },
    { name: 'Unit B', floor: 2, prefix: '2' },
  ];

  const sensorTypes: SensorType[] = ['ai-vision', 'ai-sensor', 'hybrid'];
  const sensorWeights = [70, 20, 10]; // percentage distribution

  function weightedSensorType(): SensorType {
    const roll = randomInt(1, 100);
    let cumulative = 0;
    for (let i = 0; i < sensorTypes.length; i++) {
      cumulative += sensorWeights[i];
      if (roll <= cumulative) return sensorTypes[i];
    }
    return 'ai-vision';
  }

  for (const unit of units) {
    for (let i = 1; i <= 25; i++) {
      const roomNumber = `${unit.prefix}${i.toString().padStart(2, '0')}`;
      const sensorType = weightedSensorType();
      // ~20% of rooms are semi-private
      const roomType: RoomType = randomInt(1, 100) <= 20 ? 'semi-private' : 'single';
      const now = new Date().toISOString();

      const sensors = [];
      if (sensorType === 'ai-vision' || sensorType === 'hybrid') {
        sensors.push({
          id: uuid(),
          type: 'ai-vision' as const,
          online: true,
          lastHeartbeat: now,
          healthScore: randomInt(90, 100),
        });
      }
      if (sensorType === 'ai-sensor' || sensorType === 'hybrid') {
        sensors.push({
          id: uuid(),
          type: 'ai-sensor' as const,
          online: true,
          lastHeartbeat: now,
          healthScore: randomInt(90, 100),
        });
      }

      rooms.push({
        id: uuid(),
        number: roomNumber,
        unit: unit.name,
        floor: unit.floor,
        roomType,
        sensorType,
        status: 'clear',
        statusColor: 'green',
        residents: [],
        sensors,
        lastEventAt: null,
        hasExclusionZone: i % 5 === 0,
      });
    }
  }

  return rooms;
}

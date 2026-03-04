import type { Resident, RiskTrend } from '@/types';
import type { Room } from '@/types';
import { uuid, randomInt, randomFloat, randomName, randomPick, randomDate } from '../helpers';

export function generateResidents(rooms: Room[]): Resident[] {
  const residents: Resident[] = [];
  // Occupy ~80% of rooms
  const occupiedRooms = rooms.filter((_, i) => i % 5 !== 4); // skip every 5th room

  for (const room of occupiedRooms) {
    const isSemiPrivate = room.roomType === 'semi-private';
    const residentCount = isSemiPrivate ? 2 : 1;

    for (let bed = 0; bed < residentCount; bed++) {
      const name = randomName();
      const riskScore = Math.min(100, Math.max(0, Math.round(45 + (randomFloat(-1, 1) + randomFloat(-1, 1)) * 20)));
      const trends: RiskTrend[] = ['rising', 'stable', 'declining'];
      const trend = riskScore > 60 ? randomPick(['rising', 'stable'] as RiskTrend[]) : randomPick(trends);
      const fallCount30 = riskScore > 70 ? randomInt(1, 5) : riskScore > 40 ? randomInt(0, 2) : randomInt(0, 1);
      const now = new Date();
      const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      const sixMonthsAgo = new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000);

      const bedZone = isSemiPrivate ? (bed === 0 ? 'A' as const : 'B' as const) : null;

      const resident: Resident = {
        id: uuid(),
        name: name.full,
        roomId: room.id,
        roomNumber: room.number,
        unit: room.unit,
        bedZone,
        age: randomInt(72, 96),
        riskScore,
        riskTrend: trend,
        fallCount30Days: fallCount30,
        fallCountTotal: fallCount30 + randomInt(0, 8),
        lastFallDate: fallCount30 > 0 ? randomDate(thirtyDaysAgo, now).toISOString() : null,
        lastEventDate: randomDate(thirtyDaysAgo, now).toISOString(),
        admittedAt: randomDate(sixMonthsAgo, thirtyDaysAgo).toISOString(),
        observeOnly: randomInt(1, 100) <= 15,
      };

      residents.push(resident);
      // Link room to resident
      room.residents.push({
        residentId: resident.id,
        residentName: resident.name,
        bedZone,
      });
    }
  }

  return residents;
}

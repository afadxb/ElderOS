import type { CallBellEvent, CallBellPriority, CallBellOrigin, CallBellVendor } from '@/types';
import type { Room, Resident } from '@/types';
import { uuid, randomInt, randomPick, randomDate } from '../helpers';

const STAFF_POOL = [
  { id: 'psw-1', name: 'Sarah Mitchell', role: 'psw' },
  { id: 'psw-2', name: 'James Wilson', role: 'psw' },
  { id: 'psw-3', name: 'Maria Garcia', role: 'psw' },
  { id: 'psw-4', name: 'David Thompson', role: 'psw' },
  { id: 'psw-5', name: 'Lisa Chen', role: 'psw' },
  { id: 'psw-6', name: 'Michael Brown', role: 'psw' },
  { id: 'nurse-1', name: 'Patricia Davis', role: 'nurse' },
  { id: 'nurse-2', name: 'Jennifer White', role: 'nurse' },
  { id: 'nurse-3', name: 'Amanda Taylor', role: 'nurse' },
  { id: 'nurse-4', name: 'Robert Lee', role: 'nurse' },
];

function getShiftFromHour(hour: number): 'Day' | 'Evening' | 'Night' {
  if (hour >= 7 && hour < 15) return 'Day';
  if (hour >= 15 && hour < 23) return 'Evening';
  return 'Night';
}

export function generateCallBellEvents(rooms: Room[], residents: Resident[]): CallBellEvent[] {
  const events: CallBellEvent[] = [];
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const occupiedRooms = rooms.filter(r => r.residents.length > 0);

  if (occupiedRooms.length === 0) return events;

  // Single vendor per facility (realistic)
  const vendorPool: CallBellVendor[] = ['jeron', 'rauland', 'hill-rom'];
  const facilityVendor = randomPick(vendorPool);

  for (let day = 0; day < 30; day++) {
    const dayStart = new Date(thirtyDaysAgo.getTime() + day * 24 * 60 * 60 * 1000);
    const dayEnd = new Date(dayStart.getTime() + 24 * 60 * 60 * 1000);

    // ~30 calls per day
    const callsToday = randomInt(22, 42);

    for (let i = 0; i < callsToday; i++) {
      const room = randomPick(occupiedRooms);
      const roomResidents = residents.filter(r => r.roomId === room.id);
      const resident = roomResidents.length > 0 ? randomPick(roomResidents) : null;

      const pressedAt = randomDate(dayStart, dayEnd);
      const hour = pressedAt.getHours();

      // Priority distribution: 5% emergency, 20% urgent, 75% normal
      const priorityRoll = randomInt(1, 100);
      let priority: CallBellPriority;
      if (priorityRoll <= 5) priority = 'emergency';
      else if (priorityRoll <= 25) priority = 'urgent';
      else priority = 'normal';

      // Origin distribution: 40% bedside, 30% bathroom, 15% pendant, 15% hallway
      const originRoll = randomInt(1, 100);
      let origin: CallBellOrigin;
      if (originRoll <= 40) origin = 'bedside';
      else if (originRoll <= 70) origin = 'bathroom';
      else if (originRoll <= 85) origin = 'pendant';
      else origin = 'hallway';

      // Status: 5% cancelled, 90% closed, 5% responded (still open)
      const statusRoll = randomInt(1, 100);

      if (statusRoll <= 5) {
        // Cancelled
        events.push({
          id: uuid(),
          roomId: room.id,
          roomNumber: room.number,
          residentId: resident?.id || '',
          residentName: resident?.name || 'Unknown',
          unit: room.unit,
          floor: room.floor,
          origin,
          priority,
          status: 'cancelled',
          vendor: facilityVendor,
          pressedAt: pressedAt.toISOString(),
          respondedAt: null,
          closedAt: new Date(pressedAt.getTime() + randomInt(5, 30) * 1000).toISOString(),
          responseTimeSeconds: null,
          respondedBy: null,
          respondedByName: null,
          shift: getShiftFromHour(hour),
        });
        continue;
      }

      // Staff responds — response time varies by priority and shift
      let responseDelay: number;
      if (priority === 'emergency') {
        responseDelay = randomInt(15, 90);
      } else if (priority === 'urgent') {
        responseDelay = randomInt(20, 150);
      } else {
        responseDelay = randomInt(30, 300);
        // 10% slow outliers
        if (randomInt(1, 100) <= 10) {
          responseDelay = randomInt(200, 480);
        }
      }

      // Night shift is slower
      if (hour >= 23 || hour < 7) {
        responseDelay = Math.round(responseDelay * 1.3);
      }

      const respondedAt = new Date(pressedAt.getTime() + responseDelay * 1000);
      const staff = randomPick(STAFF_POOL);

      const isClosed = statusRoll <= 95;
      const closedAt = isClosed
        ? new Date(respondedAt.getTime() + randomInt(60, 300) * 1000).toISOString()
        : null;

      events.push({
        id: uuid(),
        roomId: room.id,
        roomNumber: room.number,
        residentId: resident?.id || '',
        residentName: resident?.name || 'Unknown',
        unit: room.unit,
        floor: room.floor,
        origin,
        priority,
        status: isClosed ? 'closed' : 'responded',
        vendor: facilityVendor,
        pressedAt: pressedAt.toISOString(),
        respondedAt: respondedAt.toISOString(),
        closedAt,
        responseTimeSeconds: responseDelay,
        respondedBy: staff.id,
        respondedByName: staff.name,
        shift: getShiftFromHour(hour),
      });
    }
  }

  // Sort by pressedAt descending (newest first)
  events.sort((a, b) => new Date(b.pressedAt).getTime() - new Date(a.pressedAt).getTime());
  return events;
}

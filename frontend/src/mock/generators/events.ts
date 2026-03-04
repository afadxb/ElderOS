import type { AlertEvent, EventType, Severity, ConfidenceLevel, AlertStatus, SensorSource } from '@/types';
import type { Room } from '@/types';
import type { Resident } from '@/types';
import { uuid, randomInt, randomFloat, randomPick, randomDate, PRE_EVENT_SUMMARIES, POST_EVENT_STATES } from '../helpers';

function getConfidenceLevel(score: number): ConfidenceLevel {
  if (score >= 85) return 'high';
  if (score >= 60) return 'medium';
  return 'low';
}

function getSeverity(eventType: EventType): Severity {
  if (eventType === 'fall' || eventType === 'unsafe-transfer') return 'critical';
  return 'warning';
}

export function generateHistoricalEvents(rooms: Room[], residents: Resident[]): AlertEvent[] {
  const events: AlertEvent[] = [];
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
  const occupiedRooms = rooms.filter(r => r.residents.length > 0);

  // Generate ~17 events per day for 30 days = ~510 events
  for (let day = 0; day < 30; day++) {
    const dayStart = new Date(thirtyDaysAgo.getTime() + day * 24 * 60 * 60 * 1000);
    const dayEnd = new Date(dayStart.getTime() + 24 * 60 * 60 * 1000);

    // ~3 falls/day
    for (let i = 0; i < randomInt(2, 5); i++) {
      events.push(createEvent('fall', dayStart, dayEnd, occupiedRooms, residents));
    }
    // ~8 bed exits/day
    for (let i = 0; i < randomInt(5, 11); i++) {
      events.push(createEvent('bed-exit', dayStart, dayEnd, occupiedRooms, residents));
    }
    // ~5 inactivity/day
    for (let i = 0; i < randomInt(3, 7); i++) {
      events.push(createEvent('inactivity', dayStart, dayEnd, occupiedRooms, residents));
    }
    // ~1 unsafe transfer/day
    if (randomInt(1, 100) <= 70) {
      events.push(createEvent('unsafe-transfer', dayStart, dayEnd, occupiedRooms, residents));
    }
  }

  // Sort by detectedAt descending
  events.sort((a, b) => new Date(b.detectedAt).getTime() - new Date(a.detectedAt).getTime());
  return events;
}

function getSensorSource(room: Room): SensorSource {
  if (room.sensorType === 'hybrid') return 'fused';
  if (room.sensorType === 'ai-sensor') return 'ai-sensor';
  return 'ai-vision';
}

function createEvent(
  eventType: EventType,
  periodStart: Date,
  periodEnd: Date,
  rooms: Room[],
  residents: Resident[]
): AlertEvent {
  const room = randomPick(rooms);
  const roomResidents = residents.filter(r => r.roomId === room.id);
  const resident = roomResidents.length > 0 ? randomPick(roomResidents) : null;
  const detectedAt = randomDate(periodStart, periodEnd);
  const confidenceScore = randomInt(35, 98);
  const confidence = getConfidenceLevel(confidenceScore);

  // Most historical events are resolved
  const statusRoll = randomInt(1, 100);
  let status: AlertStatus;
  let acknowledgedAt: string | null = null;
  let resolvedAt: string | null = null;
  let acknowledgedBy: string | null = null;
  let resolvedBy: string | null = null;

  if (statusRoll <= 85) {
    status = 'resolved';
    const ackDelay = randomInt(15, 240);
    acknowledgedAt = new Date(detectedAt.getTime() + ackDelay * 1000).toISOString();
    acknowledgedBy = 'psw-' + randomInt(1, 10);
    const resolveDelay = randomInt(60, 600);
    resolvedAt = new Date(detectedAt.getTime() + (ackDelay + resolveDelay) * 1000).toISOString();
    resolvedBy = acknowledgedBy;
  } else if (statusRoll <= 95) {
    status = 'acknowledged';
    const ackDelay = randomInt(15, 240);
    acknowledgedAt = new Date(detectedAt.getTime() + ackDelay * 1000).toISOString();
    acknowledgedBy = 'psw-' + randomInt(1, 10);
  } else {
    status = 'dismissed';
  }

  const isRepeatFall = eventType === 'fall' && resident
    ? resident.fallCount30Days > 2
    : false;

  return {
    id: uuid(),
    roomId: room.id,
    roomNumber: room.number,
    residentId: resident?.id || '',
    residentName: resident?.name || 'Unknown',
    eventType,
    severity: getSeverity(eventType),
    confidence,
    confidenceScore,
    status,
    detectedAt: detectedAt.toISOString(),
    acknowledgedAt,
    resolvedAt,
    acknowledgedBy,
    resolvedBy,
    escalationLevel: (status as string) === 'active' ? randomInt(0, 2) : 0,
    preEventSummary: randomPick(PRE_EVENT_SUMMARIES),
    postEventState: randomPick(POST_EVENT_STATES),
    isRepeatFall,
    unit: room.unit,
    sensorSource: getSensorSource(room),
    bedZone: resident?.bedZone ?? null,
  };
}

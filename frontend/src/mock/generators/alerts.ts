import type { AlertEvent, EventType, SensorSource } from '@/types';
import { mockStore } from '../store';
import { uuid, randomInt, randomPick, PRE_EVENT_SUMMARIES, POST_EVENT_STATES } from '../helpers';

const EVENT_TYPES: EventType[] = ['fall', 'bed-exit', 'inactivity', 'unsafe-transfer'];
const EVENT_WEIGHTS = [20, 45, 25, 10]; // percentage distribution

function weightedEventType(): EventType {
  const roll = randomInt(1, 100);
  let cumulative = 0;
  for (let i = 0; i < EVENT_TYPES.length; i++) {
    cumulative += EVENT_WEIGHTS[i];
    if (roll <= cumulative) return EVENT_TYPES[i];
  }
  return 'bed-exit';
}

function getSensorSource(room: { sensorType: string }): SensorSource {
  if (room.sensorType === 'hybrid') return 'fused';
  if (room.sensorType === 'ai-sensor') return 'ai-sensor';
  return 'ai-vision';
}

export function generateActiveAlerts(): AlertEvent[] {
  const occupiedRooms = mockStore.rooms.filter(r => r.residents.length > 0);
  const alerts: AlertEvent[] = [];
  const count = randomInt(2, 5);

  const usedRooms = new Set<string>();
  for (let i = 0; i < count && usedRooms.size < occupiedRooms.length; i++) {
    let room;
    do {
      room = randomPick(occupiedRooms);
    } while (usedRooms.has(room.id));
    usedRooms.add(room.id);

    const residents = mockStore.residents.filter(r => r.roomId === room.id);
    const resident = residents.length > 0 ? randomPick(residents) : null;
    const eventType = weightedEventType();
    const now = new Date();
    const detectedAt = new Date(now.getTime() - randomInt(10, 300) * 1000);
    const confidenceScore = randomInt(65, 98);

    const alert: AlertEvent = {
      id: uuid(),
      roomId: room.id,
      roomNumber: room.number,
      residentId: resident?.id || '',
      residentName: resident?.name || 'Unknown',
      eventType,
      severity: eventType === 'fall' || eventType === 'unsafe-transfer' ? 'critical' : 'warning',
      confidence: confidenceScore >= 85 ? 'high' : 'medium',
      confidenceScore,
      status: 'active',
      detectedAt: detectedAt.toISOString(),
      acknowledgedAt: null,
      resolvedAt: null,
      acknowledgedBy: null,
      resolvedBy: null,
      escalationLevel: 0,
      preEventSummary: randomPick(PRE_EVENT_SUMMARIES),
      postEventState: randomPick(POST_EVENT_STATES),
      isRepeatFall: eventType === 'fall' && (resident?.fallCount30Days || 0) > 2,
      unit: room.unit,
      sensorSource: getSensorSource(room),
      bedZone: resident?.bedZone ?? null,
    };

    alerts.push(alert);
    room.status = 'active-alert';
    room.statusColor = 'red';
    room.lastEventAt = alert.detectedAt;
  }

  return alerts;
}

export function generateNextAlert(): AlertEvent | null {
  const occupiedRooms = mockStore.rooms.filter(r => r.residents.length > 0 && r.status === 'clear');
  if (occupiedRooms.length === 0) return null;

  const room = randomPick(occupiedRooms);
  const residents = mockStore.residents.filter(r => r.roomId === room.id);
  const resident = residents.length > 0 ? randomPick(residents) : null;
  const eventType = weightedEventType();
  const confidenceScore = randomInt(50, 98);

  return {
    id: uuid(),
    roomId: room.id,
    roomNumber: room.number,
    residentId: resident?.id || '',
    residentName: resident?.name || 'Unknown',
    eventType,
    severity: eventType === 'fall' || eventType === 'unsafe-transfer' ? 'critical' : 'warning',
    confidence: confidenceScore >= 85 ? 'high' : confidenceScore >= 60 ? 'medium' : 'low',
    confidenceScore,
    status: 'active',
    detectedAt: new Date().toISOString(),
    acknowledgedAt: null,
    resolvedAt: null,
    acknowledgedBy: null,
    resolvedBy: null,
    escalationLevel: 0,
    preEventSummary: randomPick(PRE_EVENT_SUMMARIES),
    postEventState: randomPick(POST_EVENT_STATES),
    isRepeatFall: eventType === 'fall' && (resident?.fallCount30Days || 0) > 2,
    unit: room.unit,
    sensorSource: getSensorSource(room),
    bedZone: resident?.bedZone ?? null,
  };
}

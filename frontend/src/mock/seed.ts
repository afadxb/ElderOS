import { mockStore } from './store';
import { resetSeed } from './helpers';
import { generateRooms } from './generators/rooms';
import { generateResidents } from './generators/residents';
import { generateHistoricalEvents } from './generators/events';
import { generateActiveAlerts } from './generators/alerts';
import { generateCameraHealth } from './generators/cameras';
import { generateSystemMetrics } from './generators/systemMetrics';
import { generateShiftSummaries } from './generators/shiftData';
import { generateCallBellEvents } from './generators/callBellData';
import { generateDevices } from './generators/devices';
import type { EscalationRule, ExclusionZone, Incident, Unit } from '@/types';
import { uuid } from './helpers';

export function seedMockData(): void {
  resetSeed(42);

  // Generate base data
  const rooms = generateRooms();
  const residents = generateResidents(rooms); // mutates rooms to link residents
  const historicalEvents = generateHistoricalEvents(rooms, residents);
  const activeAlerts = generateActiveAlerts();
  const sensorHealth = generateCameraHealth(rooms);
  const systemMetrics = generateSystemMetrics();
  const shiftSummaries = generateShiftSummaries();
  const callBellEvents = generateCallBellEvents(rooms, residents);
  const devices = generateDevices(rooms);

  // Update sensor online status on rooms
  for (const sh of sensorHealth) {
    const room = rooms.find(r => r.id === sh.roomId);
    if (room) {
      const sensor = room.sensors.find(s => s.id === sh.sensorId);
      if (sensor) {
        sensor.online = sh.status !== 'offline';
        sensor.healthScore = sh.status === 'online' ? 95 : sh.status === 'degraded' ? 60 : 0;
      }
      // Room goes offline only if ALL sensors are offline
      const allOffline = room.sensors.every(s => !s.online);
      if (allOffline) {
        room.status = 'offline';
        room.statusColor = 'gray';
      }
    }
  }

  // Create incidents from resolved/acknowledged historical events
  const incidents: Incident[] = historicalEvents
    .filter(e => e.status === 'resolved' || e.status === 'acknowledged')
    .slice(0, 200)
    .map(e => ({
      id: uuid(),
      eventId: e.id,
      roomNumber: e.roomNumber,
      residentName: e.residentName,
      residentId: e.residentId,
      eventType: e.eventType,
      confidence: e.confidence,
      confidenceScore: e.confidenceScore,
      status: e.status,
      ntpTimestamp: e.detectedAt,
      detectedAt: e.detectedAt,
      acknowledgedAt: e.acknowledgedAt,
      resolvedAt: e.resolvedAt,
      ackResponseSeconds: e.acknowledgedAt
        ? Math.round((new Date(e.acknowledgedAt).getTime() - new Date(e.detectedAt).getTime()) / 1000)
        : null,
      resolveResponseSeconds: e.resolvedAt
        ? Math.round((new Date(e.resolvedAt).getTime() - new Date(e.detectedAt).getTime()) / 1000)
        : null,
      acknowledgedBy: e.acknowledgedBy,
      resolvedBy: e.resolvedBy,
      preEventSummary: e.preEventSummary,
      postEventState: e.postEventState,
      escalationTimeline: e.escalationLevel > 0
        ? [
            {
              level: 1,
              action: 'SMS sent to Supervisor on duty',
              triggeredAt: new Date(new Date(e.detectedAt).getTime() + 120000).toISOString(),
              acknowledged: true,
            },
          ]
        : [],
      isRepeatFall: e.isRepeatFall,
      notes: '',
      unit: e.unit,
      sensorSource: e.sensorSource,
      bedZone: e.bedZone,
    }));

  // Default escalation rules
  const escalationRules: EscalationRule[] = [
    { id: uuid(), delayMinutes: 2, action: 'sms', target: 'Supervisor', enabled: true },
    { id: uuid(), delayMinutes: 5, action: 'sms', target: 'Charge Nurse', enabled: true },
    { id: uuid(), delayMinutes: 10, action: 'call', target: 'Unit Manager', enabled: false },
  ];

  // Exclusion zones for rooms with bathroom exclusion
  const exclusionZones: ExclusionZone[] = rooms
    .filter(r => r.hasExclusionZone)
    .map(r => ({
      id: uuid(),
      roomId: r.id,
      roomNumber: r.number,
      zoneName: 'Bathroom',
      enabled: true,
    }));

  // Derive units from room data
  const unitMap = new Map<string, { name: string; floor: number }>();
  for (const room of rooms) {
    if (!unitMap.has(room.unit)) {
      unitMap.set(room.unit, { name: room.unit, floor: room.floor });
    }
  }
  const units: Unit[] = Array.from(unitMap.values()).map(u => ({
    id: uuid(),
    name: u.name,
    floor: u.floor,
  }));

  // Populate store
  mockStore.units = units;
  mockStore.rooms = rooms;
  mockStore.residents = residents;
  mockStore.events = [...activeAlerts, ...historicalEvents];
  mockStore.incidents = incidents;
  mockStore.sensors = sensorHealth;
  mockStore.systemMetrics = systemMetrics;
  mockStore.shiftSummaries = shiftSummaries;
  mockStore.callBellEvents = callBellEvents;
  mockStore.devices = devices;
  mockStore.settings.escalationRules = escalationRules;
  mockStore.settings.exclusionZones = exclusionZones;
}

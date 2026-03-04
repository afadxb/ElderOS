import type { Unit, Room, SensorType, RoomType } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';
import { uuid } from '@/mock/helpers';

// ── Units ──────────────────────────────────────────────

export async function getUnits(): Promise<(Unit & { roomCount: number })[]> {
  await simulateLatency();
  return mockStore.units.map(u => ({
    ...u,
    roomCount: mockStore.rooms.filter(r => r.unit === u.name).length,
  }));
}

export async function addUnit(name: string, floor: number): Promise<Unit> {
  await simulateLatency();
  const unit: Unit = { id: uuid(), name, floor };
  mockStore.addUnit(unit);
  return unit;
}

export async function updateUnit(id: string, name: string, floor: number): Promise<void> {
  await simulateLatency();
  mockStore.updateUnit(id, name, floor);
}

export async function removeUnit(id: string): Promise<void> {
  await simulateLatency();
  mockStore.removeUnit(id);
}

// ── Rooms ──────────────────────────────────────────────

export async function getRoomsByUnit(unit?: string): Promise<Room[]> {
  await simulateLatency();
  if (!unit) return mockStore.rooms;
  return mockStore.rooms.filter(r => r.unit === unit);
}

export async function addRoom(
  unitName: string,
  floor: number,
  roomNumber: string,
  roomType: RoomType,
  sensorType: SensorType,
): Promise<Room> {
  await simulateLatency();
  const now = new Date().toISOString();
  const sensors = [];
  if (sensorType === 'ai-vision' || sensorType === 'hybrid') {
    sensors.push({ id: uuid(), type: 'ai-vision' as const, online: true, lastHeartbeat: now, healthScore: 95 });
  }
  if (sensorType === 'ai-sensor' || sensorType === 'hybrid') {
    sensors.push({ id: uuid(), type: 'ai-sensor' as const, online: true, lastHeartbeat: now, healthScore: 95 });
  }
  const room: Room = {
    id: uuid(),
    number: roomNumber,
    unit: unitName,
    floor,
    roomType,
    sensorType,
    status: 'clear',
    statusColor: 'green',
    residents: [],
    sensors,
    lastEventAt: null,
    hasExclusionZone: false,
  };
  mockStore.addRoom(room);
  return room;
}

export async function updateRoom(
  id: string,
  updates: Partial<Pick<Room, 'number' | 'roomType' | 'sensorType' | 'unit' | 'floor'>>,
): Promise<void> {
  await simulateLatency();
  mockStore.updateRoom(id, updates);
}

export async function removeRoom(id: string): Promise<void> {
  await simulateLatency();
  mockStore.removeRoom(id);
}

// ── Helpers ────────────────────────────────────────────

export async function getUnitNames(): Promise<string[]> {
  await simulateLatency();
  return mockStore.units.map(u => u.name);
}

import type { AlertEvent } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

export async function getActiveAlerts(): Promise<AlertEvent[]> {
  await simulateLatency();
  return mockStore.getActiveAlerts();
}

export async function getRecentEvents(minutes: number = 60): Promise<AlertEvent[]> {
  await simulateLatency();
  const cutoff = new Date(Date.now() - minutes * 60 * 1000);
  return mockStore.events.filter(e => new Date(e.detectedAt) >= cutoff);
}

export async function getAllEvents(limit: number = 50): Promise<AlertEvent[]> {
  await simulateLatency();
  return mockStore.events.slice(0, limit);
}

export async function getEventsByRoom(roomId: string): Promise<AlertEvent[]> {
  await simulateLatency();
  return mockStore.events.filter(e => e.roomId === roomId).slice(0, 20);
}

export async function acknowledgeAlert(eventId: string, userId: string): Promise<AlertEvent | undefined> {
  await simulateLatency();
  return mockStore.acknowledgeEvent(eventId, userId);
}

export async function resolveAlert(eventId: string, userId: string): Promise<AlertEvent | undefined> {
  await simulateLatency();
  return mockStore.resolveEvent(eventId, userId);
}

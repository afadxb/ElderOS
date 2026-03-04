import type { Room } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

export async function getRooms(unit?: string): Promise<Room[]> {
  await simulateLatency();
  if (unit) return mockStore.rooms.filter(r => r.unit === unit);
  return mockStore.rooms;
}

export async function getRoomById(roomId: string): Promise<Room | undefined> {
  await simulateLatency();
  return mockStore.rooms.find(r => r.id === roomId);
}

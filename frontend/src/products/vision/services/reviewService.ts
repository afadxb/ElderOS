import type { AlertEvent } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

export async function getReviewQueue(): Promise<AlertEvent[]> {
  await simulateLatency();
  return mockStore.getReviewQueue();
}

export async function triageEvent(eventId: string, action: 'confirm' | 'dismiss'): Promise<void> {
  await simulateLatency();
  mockStore.triageReviewItem(eventId, action);
}

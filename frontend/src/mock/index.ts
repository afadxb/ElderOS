import { seedMockData } from './seed';

let initialized = false;

export function initializeMockData(): void {
  if (initialized) return;
  seedMockData();
  initialized = true;
}

export { mockStore } from './store';

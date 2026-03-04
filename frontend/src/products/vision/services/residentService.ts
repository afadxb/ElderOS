import type { Resident } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

export async function getResidents(unit?: string): Promise<Resident[]> {
  await simulateLatency();
  if (unit) return mockStore.residents.filter(r => r.unit === unit);
  return mockStore.residents;
}

export async function getResidentById(id: string): Promise<Resident | undefined> {
  await simulateLatency();
  return mockStore.residents.find(r => r.id === id);
}

export async function getHighRiskResidents(unit?: string): Promise<Resident[]> {
  await simulateLatency();
  let residents = mockStore.residents;
  if (unit) residents = residents.filter(r => r.unit === unit);
  return residents.filter(r => r.riskScore >= 70).sort((a, b) => b.riskScore - a.riskScore);
}

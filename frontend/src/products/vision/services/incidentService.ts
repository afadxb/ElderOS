import type { Incident, PaginatedResponse } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

interface IncidentFilters {
  unit?: string;
  eventType?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}

export async function getIncidents(filters: IncidentFilters = {}): Promise<PaginatedResponse<Incident>> {
  await simulateLatency();
  let incidents = [...mockStore.incidents];

  if (filters.unit) incidents = incidents.filter(i => i.unit === filters.unit);
  if (filters.eventType) incidents = incidents.filter(i => i.eventType === filters.eventType);
  if (filters.status) incidents = incidents.filter(i => i.status === filters.status);

  const page = filters.page || 1;
  const pageSize = filters.pageSize || 20;
  const total = incidents.length;
  const totalPages = Math.ceil(total / pageSize);
  const start = (page - 1) * pageSize;
  const data = incidents.slice(start, start + pageSize);

  return { data, total, page, pageSize, totalPages };
}

export async function getIncidentById(id: string): Promise<Incident | undefined> {
  await simulateLatency();
  return mockStore.incidents.find(i => i.id === id);
}

export async function getIncidentsByResident(residentId: string): Promise<Incident[]> {
  await simulateLatency();
  return mockStore.incidents.filter(i => i.residentId === residentId).slice(0, 10);
}

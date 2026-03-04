import { useQuery } from '@tanstack/react-query';
import * as incidentService from '../services/incidentService';

interface IncidentFilters {
  unit?: string;
  eventType?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}

export function useIncidents(filters: IncidentFilters = {}) {
  return useQuery({
    queryKey: ['incidents', filters],
    queryFn: () => incidentService.getIncidents(filters),
  });
}

export function useIncident(id: string | undefined) {
  return useQuery({
    queryKey: ['incidents', id],
    queryFn: () => incidentService.getIncidentById(id!),
    enabled: !!id,
  });
}

export function useIncidentsByResident(residentId: string | undefined) {
  return useQuery({
    queryKey: ['incidents', 'by-resident', residentId],
    queryFn: () => incidentService.getIncidentsByResident(residentId!),
    enabled: !!residentId,
  });
}

import { useQuery } from '@tanstack/react-query';
import * as residentService from '../services/residentService';

export function useResidents(unit?: string) {
  return useQuery({
    queryKey: ['residents', unit],
    queryFn: () => residentService.getResidents(unit),
  });
}

export function useResident(id: string | undefined) {
  return useQuery({
    queryKey: ['residents', id],
    queryFn: () => residentService.getResidentById(id!),
    enabled: !!id,
  });
}

export function useHighRiskResidents(unit?: string) {
  return useQuery({
    queryKey: ['residents', 'high-risk', unit],
    queryFn: () => residentService.getHighRiskResidents(unit),
  });
}

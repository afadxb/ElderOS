import { useQuery } from '@tanstack/react-query';
import * as facilityService from '../services/facilityService';

export function useUnits() {
  return useQuery({
    queryKey: ['units'],
    queryFn: () => facilityService.getUnits(),
  });
}

export function useRoomsByUnit(unit?: string) {
  return useQuery({
    queryKey: ['facility-rooms', unit],
    queryFn: () => facilityService.getRoomsByUnit(unit),
  });
}

export function useUnitNames() {
  return useQuery({
    queryKey: ['unit-names'],
    queryFn: () => facilityService.getUnitNames(),
  });
}

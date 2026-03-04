import { useQuery } from '@tanstack/react-query';
import type { DeviceType } from '@/types';
import * as deviceService from '../services/deviceService';

export function useDevices(filters?: { roomId?: string; type?: DeviceType }) {
  return useQuery({
    queryKey: ['devices', filters],
    queryFn: () => deviceService.getDevices(filters),
  });
}

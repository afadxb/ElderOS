import { useQuery } from '@tanstack/react-query';
import * as systemService from '../services/systemService';

export function useSensorHealth() {
  return useQuery({
    queryKey: ['sensor-health'],
    queryFn: () => systemService.getCameraHealth(),
    refetchInterval: 30_000,
  });
}

export function useSystemMetrics() {
  return useQuery({
    queryKey: ['system-metrics'],
    queryFn: () => systemService.getSystemMetrics(),
    refetchInterval: 30_000,
  });
}

export function useSelfTestReport() {
  return useQuery({
    queryKey: ['self-test'],
    queryFn: () => systemService.getSelfTestReport(),
  });
}

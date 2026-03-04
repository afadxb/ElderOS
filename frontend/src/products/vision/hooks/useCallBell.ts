import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as callBellService from '../services/callBellService';

interface CallBellFilters {
  unit?: string;
  floor?: number;
  shift?: string;
  priority?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  pageSize?: number;
}

export function useCallBellEvents(filters: CallBellFilters = {}) {
  return useQuery({
    queryKey: ['call-bell-events', filters],
    queryFn: () => callBellService.getCallBellEvents(filters),
  });
}

export function useActiveCallBells() {
  return useQuery({
    queryKey: ['call-bell-active'],
    queryFn: () => callBellService.getActiveCallBells(),
    refetchInterval: 5000,
  });
}

export function useRespondToCallBell() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ eventId, userId, userName }: { eventId: string; userId: string; userName: string }) =>
      callBellService.respondToCallBell(eventId, userId, userName),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['call-bell-active'] });
      queryClient.invalidateQueries({ queryKey: ['call-bell-events'] });
    },
  });
}

export function useCloseCallBell() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (eventId: string) => callBellService.closeCallBell(eventId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['call-bell-active'] });
      queryClient.invalidateQueries({ queryKey: ['call-bell-events'] });
    },
  });
}

export function useCallBellStaffMetrics(filters: { unit?: string; dateFrom?: string; dateTo?: string } = {}) {
  return useQuery({
    queryKey: ['call-bell-staff-metrics', filters],
    queryFn: () => callBellService.getStaffMetrics(filters),
  });
}

export function useCallBellFloorMetrics(filters: { dateFrom?: string; dateTo?: string } = {}) {
  return useQuery({
    queryKey: ['call-bell-floor-metrics', filters],
    queryFn: () => callBellService.getFloorMetrics(filters),
  });
}

export function useCallBellShiftMetrics(filters: { unit?: string; dateFrom?: string; dateTo?: string } = {}) {
  return useQuery({
    queryKey: ['call-bell-shift-metrics', filters],
    queryFn: () => callBellService.getShiftMetrics(filters),
  });
}

export function useCallBellDailySummaries(unit?: string) {
  return useQuery({
    queryKey: ['call-bell-daily-summaries', unit],
    queryFn: () => callBellService.getDailySummaries({ unit }),
  });
}

import { useQuery } from '@tanstack/react-query';
import * as reportService from '../services/reportService';

export function useShiftSummaries(date?: string, unit?: string) {
  return useQuery({
    queryKey: ['shift-summaries', date, unit],
    queryFn: () => reportService.getShiftSummaries(date, unit),
  });
}

export function useWeeklyDigest(unit?: string) {
  return useQuery({
    queryKey: ['weekly-digest', unit],
    queryFn: () => reportService.getWeeklyDigest(unit),
  });
}

export function useBoardReportData() {
  return useQuery({
    queryKey: ['board-report'],
    queryFn: () => reportService.getBoardReportData(),
  });
}

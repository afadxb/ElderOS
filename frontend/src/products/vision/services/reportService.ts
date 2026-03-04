import type { ShiftSummary, WeeklyDigest, BoardReportData } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';
import { generateMonthlyTrends } from '@/mock/generators/responseTimeData';

export async function getShiftSummaries(date?: string, unit?: string): Promise<ShiftSummary[]> {
  await simulateLatency();
  let summaries = mockStore.shiftSummaries;
  if (date) summaries = summaries.filter(s => s.date === date);
  if (unit) summaries = summaries.filter(s => s.unit === unit);
  return summaries;
}

export async function getWeeklyDigest(unit?: string): Promise<WeeklyDigest> {
  await simulateLatency();
  const summaries = unit
    ? mockStore.shiftSummaries.filter(s => s.unit === unit)
    : mockStore.shiftSummaries;

  const totalFalls = summaries.reduce((sum, s) => sum + s.falls, 0);
  const totalEvents = summaries.reduce((sum, s) => sum + s.totalEvents, 0);

  return {
    weekStart: summaries[summaries.length - 1]?.date || '',
    weekEnd: summaries[0]?.date || '',
    unit: unit || 'All Units',
    totalFalls,
    unwitnessedFalls: Math.round(totalFalls * 0.15),
    avgResponseTimeSeconds: Math.round(summaries.reduce((s, v) => s + v.avgAckTimeSeconds, 0) / (summaries.length || 1)),
    medianResponseTimeSeconds: 85,
    repeatFallResidents: ['Margaret Smith', 'Robert Johnson'],
    complianceScore: 87,
    trendVsPriorWeek: 'improved',
  };
}

export async function getBoardReportData(): Promise<BoardReportData> {
  await simulateLatency();
  const trends = generateMonthlyTrends();
  return {
    period: 'Last 12 Months',
    facilityName: 'Maplewood Long-Term Care',
    unitSummaries: [
      { unit: 'Unit A', falls: 42, avgResponseTime: 78, unwitnessedRate: 12, complianceScore: 89 },
      { unit: 'Unit B', falls: 38, avgResponseTime: 92, unwitnessedRate: 15, complianceScore: 85 },
    ],
    liabilityIndicators: {
      slowResponses: 14,
      unacknowledgedAlerts: 6,
      repeatFalls: 8,
    },
    trendsMonthly: trends.map(t => ({
      month: t.month,
      falls: t.falls,
      avgResponseTime: t.avgResponseTime,
    })),
  };
}

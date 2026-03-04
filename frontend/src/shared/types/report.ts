export interface ShiftSummary {
  shiftId: string;
  shiftName: string;
  date: string;
  startTime: string;
  endTime: string;
  unit: string;
  totalEvents: number;
  falls: number;
  bedExits: number;
  inactivityAlerts: number;
  unsafeTransfers: number;
  avgAckTimeSeconds: number;
  avgResolveTimeSeconds: number;
  unacknowledgedCount: number;
  escalatedCount: number;
  highRiskResidents: string[];
  notableIncidents: string[];
}

export interface WeeklyDigest {
  weekStart: string;
  weekEnd: string;
  unit: string;
  totalFalls: number;
  unwitnessedFalls: number;
  avgResponseTimeSeconds: number;
  medianResponseTimeSeconds: number;
  repeatFallResidents: string[];
  complianceScore: number;
  trendVsPriorWeek: 'improved' | 'unchanged' | 'declined';
}

export interface BoardReportData {
  period: string;
  facilityName: string;
  unitSummaries: {
    unit: string;
    falls: number;
    avgResponseTime: number;
    unwitnessedRate: number;
    complianceScore: number;
  }[];
  liabilityIndicators: {
    slowResponses: number;
    unacknowledgedAlerts: number;
    repeatFalls: number;
  };
  trendsMonthly: {
    month: string;
    falls: number;
    avgResponseTime: number;
  }[];
}

export type RiskTrend = 'rising' | 'stable' | 'declining';

export interface Resident {
  id: string;
  name: string;
  roomId: string;
  roomNumber: string;
  unit: string;
  bedZone: 'A' | 'B' | null;
  age: number;
  riskScore: number;
  riskTrend: RiskTrend;
  fallCount30Days: number;
  fallCountTotal: number;
  lastFallDate: string | null;
  lastEventDate: string | null;
  admittedAt: string;
  observeOnly: boolean;
}

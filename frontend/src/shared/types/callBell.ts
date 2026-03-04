export type CallBellVendor = 'jeron' | 'rauland' | 'hill-rom';
export type CallBellStatus = 'active' | 'responded' | 'closed' | 'cancelled';
export type CallBellPriority = 'emergency' | 'urgent' | 'normal';
export type CallBellOrigin = 'bedside' | 'bathroom' | 'hallway' | 'pendant';

export interface CallBellEvent {
  id: string;
  roomId: string;
  roomNumber: string;
  residentId: string;
  residentName: string;
  unit: string;
  floor: number;
  origin: CallBellOrigin;
  priority: CallBellPriority;
  status: CallBellStatus;
  vendor: CallBellVendor;
  pressedAt: string;
  respondedAt: string | null;
  closedAt: string | null;
  responseTimeSeconds: number | null;
  respondedBy: string | null;
  respondedByName: string | null;
  shift: 'Day' | 'Evening' | 'Night';
}

export interface CallBellStaffMetrics {
  staffId: string;
  staffName: string;
  role: string;
  totalCalls: number;
  avgResponseSeconds: number;
  medianResponseSeconds: number;
  minResponseSeconds: number;
  maxResponseSeconds: number;
  callsUnder60s: number;
  callsUnder120s: number;
  callsOver180s: number;
}

export interface CallBellFloorMetrics {
  floor: number;
  unit: string;
  totalCalls: number;
  avgResponseSeconds: number;
  callsByPriority: Record<CallBellPriority, number>;
  callsByOrigin: Record<CallBellOrigin, number>;
  peakHour: number;
}

export interface CallBellShiftMetrics {
  shift: 'Day' | 'Evening' | 'Night';
  date: string;
  unit: string;
  totalCalls: number;
  avgResponseSeconds: number;
  respondedWithin60s: number;
  respondedWithin120s: number;
  slowResponses: number;
}

export interface CallBellDailySummary {
  date: string;
  totalCalls: number;
  avgResponseSeconds: number;
}

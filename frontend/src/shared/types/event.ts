export type EventType = 'fall' | 'bed-exit' | 'inactivity' | 'unsafe-transfer';
export type Severity = 'critical' | 'warning' | 'info';
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed' | 'escalated';
export type SensorSource = 'ai-vision' | 'ai-sensor' | 'fused';

export interface AlertEvent {
  id: string;
  roomId: string;
  roomNumber: string;
  residentId: string;
  residentName: string;
  eventType: EventType;
  severity: Severity;
  confidence: ConfidenceLevel;
  confidenceScore: number;
  status: AlertStatus;
  detectedAt: string;
  acknowledgedAt: string | null;
  resolvedAt: string | null;
  acknowledgedBy: string | null;
  resolvedBy: string | null;
  escalationLevel: number;
  preEventSummary: string;
  postEventState: string;
  isRepeatFall: boolean;
  unit: string;
  sensorSource: SensorSource;
  bedZone: 'A' | 'B' | null;
}

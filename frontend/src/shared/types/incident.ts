import type { EventType, AlertStatus, ConfidenceLevel } from './event';

export interface EscalationStep {
  level: number;
  action: string;
  triggeredAt: string;
  acknowledged: boolean;
}

export interface Incident {
  id: string;
  eventId: string;
  roomNumber: string;
  residentName: string;
  residentId: string;
  eventType: EventType;
  confidence: ConfidenceLevel;
  confidenceScore: number;
  status: AlertStatus;
  ntpTimestamp: string;
  detectedAt: string;
  acknowledgedAt: string | null;
  resolvedAt: string | null;
  ackResponseSeconds: number | null;
  resolveResponseSeconds: number | null;
  acknowledgedBy: string | null;
  resolvedBy: string | null;
  preEventSummary: string;
  postEventState: string;
  escalationTimeline: EscalationStep[];
  isRepeatFall: boolean;
  notes: string;
  unit: string;
  sensorSource: 'ai-vision' | 'ai-sensor' | 'fused';
  bedZone: 'A' | 'B' | null;
}

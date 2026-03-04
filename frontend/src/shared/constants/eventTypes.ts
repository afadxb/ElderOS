import type { EventType, Severity } from '@/types/event';

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  'fall': 'Fall Detected',
  'bed-exit': 'Bed Exit',
  'inactivity': 'Prolonged Inactivity',
  'unsafe-transfer': 'Unsafe Transfer',
};

export const EVENT_TYPE_SEVERITY: Record<EventType, Severity> = {
  'fall': 'critical',
  'bed-exit': 'warning',
  'inactivity': 'warning',
  'unsafe-transfer': 'critical',
};

export const SEVERITY_COLORS = {
  critical: { bg: 'bg-elder-critical-bg', text: 'text-elder-critical', border: 'border-elder-critical' },
  warning: { bg: 'bg-elder-warning-bg', text: 'text-elder-warning', border: 'border-elder-warning' },
  info: { bg: 'bg-elder-ok-bg', text: 'text-elder-ok', border: 'border-elder-ok' },
} as const;

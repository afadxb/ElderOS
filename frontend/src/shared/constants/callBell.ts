import type { CallBellPriority, CallBellOrigin, CallBellStatus, CallBellVendor } from '@/types';

export const CALL_BELL_THRESHOLDS = {
  responseGoodSeconds: 60,
  responseWarningSeconds: 120,
  responseCriticalSeconds: 180,
  emergencyMaxSeconds: 60,
  complianceTargetPercent: 90,
} as const;

export const CALL_BELL_PRIORITY_LABELS: Record<CallBellPriority, string> = {
  emergency: 'Emergency',
  urgent: 'Urgent',
  normal: 'Normal',
};

export const CALL_BELL_PRIORITY_COLORS: Record<CallBellPriority, { bg: string; text: string }> = {
  emergency: { bg: 'bg-red-100', text: 'text-red-700' },
  urgent: { bg: 'bg-amber-100', text: 'text-amber-700' },
  normal: { bg: 'bg-blue-100', text: 'text-blue-700' },
};

export const CALL_BELL_ORIGIN_LABELS: Record<CallBellOrigin, string> = {
  bedside: 'Bedside',
  bathroom: 'Bathroom',
  hallway: 'Hallway',
  pendant: 'Pendant',
};

export const CALL_BELL_STATUS_LABELS: Record<CallBellStatus, string> = {
  active: 'Active',
  responded: 'Responded',
  closed: 'Closed',
  cancelled: 'Cancelled',
};

export const CALL_BELL_VENDOR_LABELS: Record<CallBellVendor, string> = {
  jeron: 'Jeron',
  rauland: 'Rauland',
  'hill-rom': 'Hill-Rom',
};

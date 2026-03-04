import type { Severity, RoomStatusColor, AlertStatus } from '@/types';

export function severityToColor(severity: Severity): string {
  const map: Record<Severity, string> = {
    critical: 'text-elder-critical',
    warning: 'text-elder-warning',
    info: 'text-elder-ok',
  };
  return map[severity];
}

export function severityToBg(severity: Severity): string {
  const map: Record<Severity, string> = {
    critical: 'bg-elder-critical-bg',
    warning: 'bg-elder-warning-bg',
    info: 'bg-elder-ok-bg',
  };
  return map[severity];
}

export function roomStatusToBg(color: RoomStatusColor): string {
  const map: Record<RoomStatusColor, string> = {
    red: 'bg-elder-critical',
    yellow: 'bg-elder-warning',
    green: 'bg-elder-ok',
    gray: 'bg-gray-400',
  };
  return map[color];
}

export function alertStatusToBadge(status: AlertStatus): { label: string; className: string } {
  const map: Record<AlertStatus, { label: string; className: string }> = {
    active: { label: 'Active', className: 'bg-red-100 text-red-800' },
    acknowledged: { label: 'Acknowledged', className: 'bg-blue-100 text-blue-800' },
    resolved: { label: 'Resolved', className: 'bg-green-100 text-green-800' },
    dismissed: { label: 'Dismissed', className: 'bg-gray-100 text-gray-600' },
    escalated: { label: 'Escalated', className: 'bg-amber-100 text-amber-800' },
  };
  return map[status];
}

export function riskScoreToColor(score: number): string {
  if (score >= 71) return 'text-elder-critical';
  if (score >= 41) return 'text-elder-warning';
  return 'text-elder-ok';
}

export function riskScoreToBg(score: number): string {
  if (score >= 71) return 'bg-elder-critical-bg';
  if (score >= 41) return 'bg-elder-warning-bg';
  return 'bg-elder-ok-bg';
}

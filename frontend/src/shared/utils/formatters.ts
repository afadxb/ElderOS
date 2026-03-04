import { format, formatDistanceToNow, differenceInSeconds } from 'date-fns';

export function formatTimestamp(iso: string): string {
  return format(new Date(iso), 'MMM d, yyyy HH:mm:ss');
}

export function formatTime(iso: string): string {
  return format(new Date(iso), 'HH:mm:ss');
}

export function formatDate(iso: string): string {
  return format(new Date(iso), 'MMM d, yyyy');
}

export function formatRelative(iso: string): string {
  return formatDistanceToNow(new Date(iso), { addSuffix: true });
}

export function formatResponseTime(seconds: number | null): string {
  if (seconds === null) return '--';
  if (seconds < 60) return `${seconds}s`;
  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;
  return `${min}m ${sec}s`;
}

export function formatPercentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function formatCountdown(totalSeconds: number): string {
  const min = Math.floor(Math.abs(totalSeconds) / 60);
  const sec = Math.abs(totalSeconds) % 60;
  return `${min}:${sec.toString().padStart(2, '0')}`;
}

export function responseTimeToSeconds(
  detectedAt: string,
  respondedAt: string | null
): number | null {
  if (!respondedAt) return null;
  return differenceInSeconds(new Date(respondedAt), new Date(detectedAt));
}

import { cn } from '@/utils/cn';
import { formatResponseTime } from '@/utils/formatters';

interface ResponseTimeBadgeProps {
  label: 'Ack' | 'Resolve';
  seconds: number | null;
  thresholdSeconds: number;
}

export function ResponseTimeBadge({ label, seconds, thresholdSeconds }: ResponseTimeBadgeProps) {
  const isOver = seconds !== null && seconds > thresholdSeconds;

  return (
    <div className={cn(
      'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-sm font-medium',
      seconds === null ? 'bg-gray-100 text-gray-500' : isOver ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
    )}>
      <span className="text-xs font-normal opacity-70">{label}:</span>
      <span className="font-mono">{formatResponseTime(seconds)}</span>
    </div>
  );
}

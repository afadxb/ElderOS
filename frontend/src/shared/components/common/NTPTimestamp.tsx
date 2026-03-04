import { formatTimestamp } from '@/utils/formatters';
import { cn } from '@/utils/cn';

interface NTPTimestampProps {
  timestamp: string;
  className?: string;
}

export function NTPTimestamp({ timestamp, className }: NTPTimestampProps) {
  return (
    <time className={cn('font-mono text-xs text-elder-text-secondary', className)} dateTime={timestamp}>
      {formatTimestamp(timestamp)}
    </time>
  );
}

import { useState } from 'react';
import { formatRelative } from '@/utils/formatters';
import { useInterval } from '@/hooks/useInterval';
import { cn } from '@/utils/cn';

interface RelativeTimeProps {
  timestamp: string;
  className?: string;
}

export function RelativeTime({ timestamp, className }: RelativeTimeProps) {
  const [display, setDisplay] = useState(formatRelative(timestamp));
  useInterval(() => setDisplay(formatRelative(timestamp)), 10000);

  return (
    <time className={cn('text-xs text-elder-text-secondary', className)} dateTime={timestamp} title={timestamp}>
      {display}
    </time>
  );
}

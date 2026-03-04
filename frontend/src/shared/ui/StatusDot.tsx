import { cn } from '@/utils/cn';

type StatusDotColor = 'green' | 'yellow' | 'red' | 'gray';

interface StatusDotProps {
  color: StatusDotColor;
  pulse?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const colorMap: Record<StatusDotColor, string> = {
  green: 'bg-elder-ok',
  yellow: 'bg-elder-warning',
  red: 'bg-elder-critical',
  gray: 'bg-gray-400',
};

const sizeMap = {
  sm: 'h-2 w-2',
  md: 'h-2.5 w-2.5',
  lg: 'h-3 w-3',
};

export function StatusDot({ color, pulse, size = 'md', className }: StatusDotProps) {
  return (
    <span className={cn('relative inline-flex', sizeMap[size], className)}>
      {pulse && (
        <span className={cn('animate-ping absolute inline-flex h-full w-full rounded-full opacity-75', colorMap[color])} />
      )}
      <span className={cn('relative inline-flex rounded-full', sizeMap[size], colorMap[color])} />
    </span>
  );
}

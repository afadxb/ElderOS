import { cn } from '@/utils/cn';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'rectangular' | 'circular';
  width?: string;
  height?: string;
}

export function Skeleton({ className, variant = 'text', width, height }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse bg-gray-200',
        variant === 'text' && 'h-4 rounded',
        variant === 'rectangular' && 'rounded-lg',
        variant === 'circular' && 'rounded-full',
        className
      )}
      style={{ width, height }}
    />
  );
}

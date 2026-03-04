import { cn } from '@/utils/cn';
import type { ReactNode } from 'react';

type BadgeVariant = 'default' | 'critical' | 'warning' | 'success' | 'info';

interface BadgeProps {
  variant?: BadgeVariant;
  children: ReactNode;
  className?: string;
  dot?: boolean;
  pulse?: boolean;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-gray-100 text-gray-700',
  critical: 'bg-red-100 text-red-800',
  warning: 'bg-amber-100 text-amber-800',
  success: 'bg-green-100 text-green-800',
  info: 'bg-blue-100 text-blue-800',
};

export function Badge({ variant = 'default', children, className, dot, pulse }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium',
        variantStyles[variant],
        className
      )}
    >
      {dot && (
        <span className="relative flex h-2 w-2">
          {pulse && (
            <span className={cn(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              variant === 'critical' ? 'bg-red-500' : variant === 'warning' ? 'bg-amber-500' : 'bg-gray-500'
            )} />
          )}
          <span className={cn(
            'relative inline-flex rounded-full h-2 w-2',
            variant === 'critical' ? 'bg-red-600' : variant === 'warning' ? 'bg-amber-600' : variant === 'success' ? 'bg-green-600' : 'bg-gray-600'
          )} />
        </span>
      )}
      {children}
    </span>
  );
}

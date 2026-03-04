import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
      <div className="text-elder-text-muted mb-3">
        {icon || <Inbox className="h-12 w-12 mx-auto" />}
      </div>
      <h3 className="text-sm font-medium text-elder-text-primary mb-1">{title}</h3>
      {description && <p className="text-sm text-elder-text-secondary max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

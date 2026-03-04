import { cn } from '@/utils/cn';
import type { ReactNode } from 'react';

interface TableProps {
  children: ReactNode;
  className?: string;
}

export function Table({ children, className }: TableProps) {
  return (
    <div className="overflow-x-auto">
      <table className={cn('w-full text-sm', className)}>
        {children}
      </table>
    </div>
  );
}

export function TableHeader({ children, className }: TableProps) {
  return <thead className={cn('border-b border-elder-border', className)}>{children}</thead>;
}

export function TableBody({ children, className }: TableProps) {
  return <tbody className={cn('divide-y divide-elder-border', className)}>{children}</tbody>;
}

export function TableRow({ children, className, onClick }: TableProps & { onClick?: () => void }) {
  return (
    <tr
      className={cn('hover:bg-elder-surface-alt transition-colors', onClick && 'cursor-pointer', className)}
      onClick={onClick}
    >
      {children}
    </tr>
  );
}

export function TableHead({ children, className }: TableProps) {
  return (
    <th className={cn('px-4 py-3 text-left text-xs font-medium text-elder-text-secondary uppercase tracking-wider', className)}>
      {children}
    </th>
  );
}

export function TableCell({ children, className }: TableProps) {
  return <td className={cn('px-4 py-3 text-sm text-elder-text-primary whitespace-nowrap', className)}>{children}</td>;
}

import type { CallBellPriority } from '@/types';
import { CALL_BELL_PRIORITY_LABELS, CALL_BELL_PRIORITY_COLORS } from '@/constants/callBell';
import { cn } from '@/utils/cn';

interface CallBellPriorityBadgeProps {
  priority: CallBellPriority;
}

export function CallBellPriorityBadge({ priority }: CallBellPriorityBadgeProps) {
  const colors = CALL_BELL_PRIORITY_COLORS[priority];
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        colors.bg,
        colors.text
      )}
    >
      {CALL_BELL_PRIORITY_LABELS[priority]}
    </span>
  );
}

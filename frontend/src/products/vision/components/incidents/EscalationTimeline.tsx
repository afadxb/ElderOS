import type { EscalationStep } from '@/types';
import { cn } from '@/utils/cn';
import { formatTime } from '@/utils/formatters';
import { CheckCircle, Clock } from 'lucide-react';

interface EscalationTimelineProps {
  steps: EscalationStep[];
}

export function EscalationTimeline({ steps }: EscalationTimelineProps) {
  if (steps.length === 0) {
    return <p className="text-sm text-elder-text-muted">No escalation triggered</p>;
  }

  return (
    <div className="space-y-2">
      {steps.map((step, i) => (
        <div key={i} className="flex items-center gap-2 text-sm">
          {step.acknowledged ? (
            <CheckCircle className="h-4 w-4 text-elder-ok flex-shrink-0" />
          ) : (
            <Clock className="h-4 w-4 text-elder-warning flex-shrink-0" />
          )}
          <span className="flex-1">{step.action}</span>
          <span className="font-mono text-xs text-elder-text-muted">{formatTime(step.triggeredAt)}</span>
        </div>
      ))}
    </div>
  );
}

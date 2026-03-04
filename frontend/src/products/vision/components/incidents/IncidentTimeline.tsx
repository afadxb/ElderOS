import { cn } from '@/utils/cn';
import { formatTime } from '@/utils/formatters';

interface TimelineStep {
  timestamp: string;
  label: string;
  type: 'detection' | 'acknowledgment' | 'escalation' | 'resolution';
}

interface IncidentTimelineProps {
  steps: TimelineStep[];
}

const dotColors = {
  detection: 'bg-elder-critical',
  acknowledgment: 'bg-elder-action',
  escalation: 'bg-elder-warning',
  resolution: 'bg-elder-ok',
};

export function IncidentTimeline({ steps }: IncidentTimelineProps) {
  return (
    <div className="relative">
      <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-elder-border" />
      <div className="space-y-4">
        {steps.map((step, i) => (
          <div key={i} className="relative flex items-start gap-3 pl-1">
            <div className={cn('relative z-10 mt-1 h-3 w-3 rounded-full ring-2 ring-white flex-shrink-0', dotColors[step.type])} />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-elder-text-primary">{step.label}</p>
              <p className="text-xs font-mono text-elder-text-muted">{formatTime(step.timestamp)}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

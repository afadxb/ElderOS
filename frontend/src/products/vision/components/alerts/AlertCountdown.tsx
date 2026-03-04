import { useCountdown } from '@/hooks/useCountdown';
import { cn } from '@/utils/cn';

interface AlertCountdownProps {
  detectedAt: string;
  escalationThresholdSeconds: number;
  isAcknowledged: boolean;
}

export function AlertCountdown({ detectedAt, escalationThresholdSeconds, isAcknowledged }: AlertCountdownProps) {
  const { elapsed, remaining, isExpired, formatted } = useCountdown(escalationThresholdSeconds, detectedAt);

  if (isAcknowledged) {
    return (
      <div className="text-center">
        <span className="text-sm text-elder-text-secondary">Acknowledged</span>
        <p className="text-lg font-mono font-semibold text-elder-action">{formatted} elapsed</p>
      </div>
    );
  }

  return (
    <div className="text-center">
      {isExpired ? (
        <>
          <span className="text-sm text-elder-critical font-medium">Escalation triggered</span>
          <p className="text-2xl font-mono font-bold text-elder-critical animate-pulse-critical">{formatted}</p>
        </>
      ) : (
        <>
          <span className="text-sm text-elder-text-secondary">Escalating in</span>
          <p className={cn(
            'text-2xl font-mono font-bold',
            remaining <= 30 ? 'text-elder-critical animate-pulse-critical' : 'text-elder-warning'
          )}>
            {formatted}
          </p>
        </>
      )}
    </div>
  );
}

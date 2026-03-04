import { cn } from '@/utils/cn';

interface MetricGaugeProps {
  label: string;
  value: number;
  max: number;
  unit?: string;
  warningThreshold?: number;
  criticalThreshold?: number;
}

export function MetricGauge({ label, value, max, unit = '%', warningThreshold = 70, criticalThreshold = 90 }: MetricGaugeProps) {
  const percentage = (value / max) * 100;
  const color = percentage >= criticalThreshold ? 'bg-elder-critical' : percentage >= warningThreshold ? 'bg-elder-warning' : 'bg-elder-ok';
  const textColor = percentage >= criticalThreshold ? 'text-elder-critical' : percentage >= warningThreshold ? 'text-elder-warning' : 'text-elder-ok';

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-elder-text-secondary">{label}</span>
        <span className={cn('font-mono font-semibold', textColor)}>{value.toFixed(1)}{unit}</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className={cn('h-full rounded-full transition-all', color)} style={{ width: `${Math.min(percentage, 100)}%` }} />
      </div>
    </div>
  );
}

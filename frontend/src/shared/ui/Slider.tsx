import { cn } from '@/utils/cn';

interface SliderProps {
  value: number;
  min: number;
  max: number;
  step?: number;
  onChange: (value: number) => void;
  label?: string;
  showValue?: boolean;
  className?: string;
}

export function Slider({ value, min, max, step = 1, onChange, label, showValue = true, className }: SliderProps) {
  return (
    <div className={cn('space-y-1', className)}>
      {(label || showValue) && (
        <div className="flex items-center justify-between">
          {label && <label className="text-sm font-medium text-elder-text-primary">{label}</label>}
          {showValue && <span className="text-sm text-elder-text-secondary">{value}</span>}
        </div>
      )}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-elder-action"
      />
    </div>
  );
}

import { Input } from '@/components/ui';

interface DateRangePickerProps {
  startDate: string;
  endDate: string;
  onStartChange: (date: string) => void;
  onEndChange: (date: string) => void;
}

export function DateRangePicker({ startDate, endDate, onStartChange, onEndChange }: DateRangePickerProps) {
  return (
    <div className="flex items-center gap-2">
      <Input type="date" value={startDate} onChange={e => onStartChange(e.target.value)} className="w-36" />
      <span className="text-sm text-elder-text-muted">to</span>
      <Input type="date" value={endDate} onChange={e => onEndChange(e.target.value)} className="w-36" />
    </div>
  );
}

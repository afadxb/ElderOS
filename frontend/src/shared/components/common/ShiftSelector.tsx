import { Select } from '@/components/ui';
import type { ShiftName } from '@/utils/dateUtils';

interface ShiftSelectorProps {
  value: ShiftName | 'all';
  onChange: (shift: ShiftName | 'all') => void;
}

export function ShiftSelector({ value, onChange }: ShiftSelectorProps) {
  return (
    <Select
      value={value}
      onChange={e => onChange(e.target.value as ShiftName | 'all')}
      options={[
        { value: 'all', label: 'All Shifts' },
        { value: 'Day', label: 'Day (07:00-15:00)' },
        { value: 'Evening', label: 'Evening (15:00-23:00)' },
        { value: 'Night', label: 'Night (23:00-07:00)' },
      ]}
    />
  );
}

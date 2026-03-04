import { useState, useEffect } from 'react';
import { Select } from '@/components/ui';
import { getUnitNames } from '@/products/vision/services/facilityService';

interface UnitSelectorProps {
  value: string;
  onChange: (unit: string) => void;
}

export function UnitSelector({ value, onChange }: UnitSelectorProps) {
  const [unitNames, setUnitNames] = useState<string[]>([]);

  useEffect(() => {
    getUnitNames().then(setUnitNames);
  }, []);

  return (
    <Select
      value={value}
      onChange={e => onChange(e.target.value)}
      options={[
        { value: '', label: 'All Units' },
        ...unitNames.map(name => ({ value: name, label: name })),
      ]}
    />
  );
}

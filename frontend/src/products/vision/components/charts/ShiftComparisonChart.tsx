import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { CHART_COLORS } from '@/constants/design-tokens';
import type { ShiftSummary } from '@/types';
import { useMemo } from 'react';

interface ShiftComparisonChartProps {
  summaries: ShiftSummary[];
}

export function ShiftComparisonChart({ summaries }: ShiftComparisonChartProps) {
  const data = useMemo(() => {
    const shifts = ['Day', 'Evening', 'Night'];
    return shifts.map(shift => {
      const shiftData = summaries.filter(s => s.shiftName === shift);
      const totalFalls = shiftData.reduce((sum, s) => sum + s.falls, 0);
      const totalBedExits = shiftData.reduce((sum, s) => sum + s.bedExits, 0);
      const avgAck = shiftData.length > 0
        ? Math.round(shiftData.reduce((sum, s) => sum + s.avgAckTimeSeconds, 0) / shiftData.length)
        : 0;

      return { shift, falls: totalFalls, bedExits: totalBedExits, avgAckTime: avgAck };
    });
  }, [summaries]);

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="shift" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis tick={{ fontSize: 11 }} stroke="#9CA3AF" allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="falls" fill={CHART_COLORS.falls} radius={[4, 4, 0, 0]} name="Falls" />
        <Bar dataKey="bedExits" fill={CHART_COLORS.bedExits} radius={[4, 4, 0, 0]} name="Bed Exits" />
      </BarChart>
    </ResponsiveContainer>
  );
}

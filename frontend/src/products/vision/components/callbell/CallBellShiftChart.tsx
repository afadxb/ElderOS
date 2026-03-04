import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import type { CallBellShiftMetrics } from '@/types';
import { CHART_COLORS, COLORS } from '@/constants/design-tokens';

interface CallBellShiftChartProps {
  data: CallBellShiftMetrics[];
}

export function CallBellShiftChart({ data }: CallBellShiftChartProps) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="shift" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis tick={{ fontSize: 11 }} stroke="#9CA3AF" allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="totalCalls" fill={CHART_COLORS.callBell} radius={[4, 4, 0, 0]} name="Total Calls" />
        <Bar dataKey="slowResponses" fill={COLORS.critical} radius={[4, 4, 0, 0]} name="Slow (>3m)" />
      </BarChart>
    </ResponsiveContainer>
  );
}

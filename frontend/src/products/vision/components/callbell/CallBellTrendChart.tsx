import { ComposedChart, Bar, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import type { CallBellDailySummary } from '@/types';
import { CHART_COLORS } from '@/constants/design-tokens';
import { format, parseISO } from 'date-fns';

interface CallBellTrendChartProps {
  data: CallBellDailySummary[];
}

export function CallBellTrendChart({ data }: CallBellTrendChartProps) {
  const chartData = data.map(d => ({
    ...d,
    label: format(parseISO(d.date), 'MMM d'),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: -10, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis yAxisId="left" tick={{ fontSize: 11 }} stroke="#9CA3AF" allowDecimals={false} label={{ value: 'Calls', angle: -90, position: 'insideLeft', style: { fontSize: 11 } }} />
        <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} stroke="#9CA3AF" label={{ value: 'Response (s)', angle: 90, position: 'insideRight', style: { fontSize: 11 } }} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar yAxisId="left" dataKey="totalCalls" fill={CHART_COLORS.callBell} radius={[4, 4, 0, 0]} name="Daily Calls" />
        <Line yAxisId="right" type="monotone" dataKey="avgResponseSeconds" stroke={CHART_COLORS.responseTime} strokeWidth={2} dot={{ r: 3 }} name="Avg Response (s)" />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

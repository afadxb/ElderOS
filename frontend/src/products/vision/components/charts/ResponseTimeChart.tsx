import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { CHART_COLORS } from '@/constants/design-tokens';
import type { ResponseTimeBucket } from '@/mock/generators/responseTimeData';

interface ResponseTimeChartProps {
  data: ResponseTimeBucket[];
  medianSeconds?: number;
}

export function ResponseTimeChart({ data, medianSeconds = 90 }: ResponseTimeChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="range" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis tick={{ fontSize: 11 }} stroke="#9CA3AF" allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Bar dataKey="count" fill={CHART_COLORS.responseTime} radius={[4, 4, 0, 0]} name="Events" />
      </BarChart>
    </ResponsiveContainer>
  );
}

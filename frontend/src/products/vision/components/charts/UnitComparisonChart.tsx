import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { CHART_COLORS } from '@/constants/design-tokens';

interface UnitComparisonData {
  unit: string;
  falls: number;
  avgResponseTime: number;
  complianceScore: number;
}

interface UnitComparisonChartProps {
  data: UnitComparisonData[];
}

export function UnitComparisonChart({ data }: UnitComparisonChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="unit" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="falls" fill={CHART_COLORS.falls} radius={[4, 4, 0, 0]} name="Falls" />
        <Bar dataKey="avgResponseTime" fill={CHART_COLORS.responseTime} radius={[4, 4, 0, 0]} name="Avg Response (s)" />
      </BarChart>
    </ResponsiveContainer>
  );
}

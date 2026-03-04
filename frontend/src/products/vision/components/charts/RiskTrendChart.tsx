import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { CHART_COLORS } from '@/constants/design-tokens';

interface RiskTrendData {
  date: string;
  score: number;
}

interface RiskTrendChartProps {
  data: RiskTrendData[];
  title?: string;
}

export function RiskTrendChart({ data }: RiskTrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Line type="monotone" dataKey="score" stroke={CHART_COLORS.risk} strokeWidth={2} dot={{ r: 3 }} name="Risk Score" />
      </LineChart>
    </ResponsiveContainer>
  );
}

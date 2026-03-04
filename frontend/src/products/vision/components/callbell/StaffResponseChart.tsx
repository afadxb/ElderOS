import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import type { CallBellStaffMetrics } from '@/types';
import { COLORS } from '@/constants/design-tokens';

interface StaffResponseChartProps {
  data: CallBellStaffMetrics[];
}

function getBarColor(seconds: number): string {
  if (seconds <= 60) return COLORS.ok;
  if (seconds <= 120) return COLORS.warning;
  return COLORS.critical;
}

export function StaffResponseChart({ data }: StaffResponseChartProps) {
  const chartData = data.map(d => ({
    name: d.staffName,
    avg: d.avgResponseSeconds,
    role: d.role,
  }));

  return (
    <ResponsiveContainer width="100%" height={Math.max(250, data.length * 40)}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis type="number" tick={{ fontSize: 11 }} stroke="#9CA3AF" unit="s" />
        <YAxis dataKey="name" type="category" tick={{ fontSize: 11 }} stroke="#9CA3AF" width={75} />
        <Tooltip
          contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}
          formatter={(value: number) => [`${value}s`, 'Avg Response']}
        />
        <Bar dataKey="avg" radius={[0, 4, 4, 0]} name="Avg Response (s)">
          {chartData.map((entry, index) => (
            <Cell key={index} fill={getBarColor(entry.avg)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

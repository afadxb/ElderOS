import { useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { CHART_COLORS } from '@/constants/design-tokens';
import type { AlertEvent } from '@/types';
import { format, subMinutes } from 'date-fns';

interface AlertTimelineProps {
  events: AlertEvent[];
}

export function AlertTimeline({ events }: AlertTimelineProps) {
  const data = useMemo(() => {
    const now = new Date();
    const buckets: { time: string; falls: number; bedExits: number; inactivity: number; transfers: number }[] = [];

    for (let i = 12; i >= 0; i--) {
      const bucketStart = subMinutes(now, i * 5);
      const bucketEnd = subMinutes(now, (i - 1) * 5);
      const timeLabel = format(bucketStart, 'HH:mm');

      const inBucket = events.filter(e => {
        const t = new Date(e.detectedAt);
        return t >= bucketStart && t < bucketEnd;
      });

      buckets.push({
        time: timeLabel,
        falls: inBucket.filter(e => e.eventType === 'fall').length,
        bedExits: inBucket.filter(e => e.eventType === 'bed-exit').length,
        inactivity: inBucket.filter(e => e.eventType === 'inactivity').length,
        transfers: inBucket.filter(e => e.eventType === 'unsafe-transfer').length,
      });
    }

    return buckets;
  }, [events]);

  return (
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis dataKey="time" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
        <YAxis tick={{ fontSize: 11 }} stroke="#9CA3AF" allowDecimals={false} />
        <Tooltip contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }} />
        <Area type="monotone" dataKey="falls" stackId="1" stroke={CHART_COLORS.falls} fill={CHART_COLORS.falls} fillOpacity={0.6} name="Falls" />
        <Area type="monotone" dataKey="bedExits" stackId="1" stroke={CHART_COLORS.bedExits} fill={CHART_COLORS.bedExits} fillOpacity={0.6} name="Bed Exits" />
        <Area type="monotone" dataKey="inactivity" stackId="1" stroke={CHART_COLORS.inactivity} fill={CHART_COLORS.inactivity} fillOpacity={0.6} name="Inactivity" />
        <Area type="monotone" dataKey="transfers" stackId="1" stroke={CHART_COLORS.unsafeTransfers} fill={CHART_COLORS.unsafeTransfers} fillOpacity={0.6} name="Transfers" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

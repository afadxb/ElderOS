import { useMemo } from 'react';
import type { Room, AlertEvent } from '@/types';
import { cn } from '@/utils/cn';
import { Tooltip } from '@/components/ui';

interface RoomHeatmapProps {
  rooms: Room[];
  events: AlertEvent[];
}

export function RoomHeatmap({ rooms, events }: RoomHeatmapProps) {
  const eventCounts = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const event of events) {
      counts[event.roomId] = (counts[event.roomId] || 0) + 1;
    }
    return counts;
  }, [events]);

  const maxCount = Math.max(1, ...Object.values(eventCounts));

  return (
    <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-1">
      {rooms.map(room => {
        const count = eventCounts[room.id] || 0;
        const intensity = count / maxCount;
        const bgColor = count === 0
          ? 'bg-gray-100'
          : intensity > 0.7
            ? 'bg-red-500'
            : intensity > 0.4
              ? 'bg-red-300'
              : intensity > 0.2
                ? 'bg-red-200'
                : 'bg-red-100';

        return (
          <Tooltip key={room.id} content={`Room ${room.number}: ${count} events`}>
            <div
              className={cn(
                'flex items-center justify-center h-10 rounded text-xs font-mono transition-colors',
                bgColor,
                count > 0 ? 'text-white' : 'text-gray-400'
              )}
            >
              {room.number}
            </div>
          </Tooltip>
        );
      })}
    </div>
  );
}

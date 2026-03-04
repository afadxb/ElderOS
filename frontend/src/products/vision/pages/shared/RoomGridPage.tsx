import { useState, useEffect } from 'react';
import { RoomStatusGrid } from '@/components/rooms/RoomStatusGrid';
import { PageHeader } from '@/components/common/PageHeader';
import { UnitSelector } from '@/components/common/UnitSelector';
import { Card, CardContent, Spinner, Badge } from '@/components/ui';
import * as roomService from '@/services/roomService';
import type { Room } from '@/types';

export function RoomGridPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [unit, setUnit] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await roomService.getRooms(unit || undefined);
      setRooms(data);
      setLoading(false);
    }
    load();
  }, [unit]);

  const statusCounts = {
    clear: rooms.filter(r => r.statusColor === 'green').length,
    attention: rooms.filter(r => r.statusColor === 'yellow').length,
    alert: rooms.filter(r => r.statusColor === 'red').length,
    offline: rooms.filter(r => r.statusColor === 'gray').length,
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Room Grid" subtitle="Real-time room status overview" actions={<UnitSelector value={unit} onChange={setUnit} />} />

      <div className="flex items-center gap-3 text-xs">
        <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-elder-ok" /> Clear ({statusCounts.clear})</div>
        <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-elder-warning" /> Attention ({statusCounts.attention})</div>
        <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-elder-critical" /> Active Alert ({statusCounts.alert})</div>
        <div className="flex items-center gap-1.5"><span className="w-3 h-3 rounded bg-gray-400" /> Offline ({statusCounts.offline})</div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Spinner size="lg" /></div>
      ) : (
        <RoomStatusGrid rooms={rooms} />
      )}
    </div>
  );
}

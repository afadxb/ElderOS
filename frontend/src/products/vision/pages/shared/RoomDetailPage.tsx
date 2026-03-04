import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { RoomDetailPanel } from '@/components/rooms/RoomDetailPanel';
import { PageHeader } from '@/components/common/PageHeader';
import { Button, Spinner } from '@/components/ui';
import { ArrowLeft } from 'lucide-react';
import * as roomService from '@/services/roomService';
import * as alertService from '@/services/alertService';
import type { Room, AlertEvent } from '@/types';

export function RoomDetailPage() {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const [room, setRoom] = useState<Room | null>(null);
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!roomId) return;
      const [r, e] = await Promise.all([
        roomService.getRoomById(roomId),
        alertService.getEventsByRoom(roomId),
      ]);
      setRoom(r || null);
      setEvents(e);
      setLoading(false);
    }
    load();
  }, [roomId]);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  if (!room) return <div className="text-center py-12"><p>Room not found</p></div>;

  return (
    <div className="max-w-2xl mx-auto space-y-4">
      <PageHeader
        title={`Room ${room.number}`}
        subtitle={room.unit}
        actions={
          <Button variant="ghost" size="sm" onClick={() => navigate('/vision/rooms')}>
            <ArrowLeft className="h-4 w-4 mr-1" /> Back
          </Button>
        }
      />
      <RoomDetailPanel room={room} events={events} />
    </div>
  );
}

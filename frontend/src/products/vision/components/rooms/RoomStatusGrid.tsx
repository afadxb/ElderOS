import type { Room } from '@/types';
import { RoomCard } from './RoomCard';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/utils/cn';

interface RoomStatusGridProps {
  rooms: Room[];
  compact?: boolean;
}

export function RoomStatusGrid({ rooms, compact }: RoomStatusGridProps) {
  const navigate = useNavigate();

  return (
    <div className={cn(
      'grid gap-2',
      compact
        ? 'grid-cols-5 sm:grid-cols-6 md:grid-cols-8'
        : 'grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 xl:grid-cols-8'
    )}>
      {rooms.map(room => (
        <RoomCard key={room.id} room={room} onClick={() => navigate(`/vision/rooms/${room.id}`)} />
      ))}
    </div>
  );
}

import type { Room, SensorType } from '@/types';
import { cn } from '@/utils/cn';
import { WifiOff, Camera, Radio } from 'lucide-react';

interface RoomCardProps {
  room: Room;
  onClick: () => void;
}

const statusBgMap = {
  green: 'bg-elder-ok hover:bg-green-600',
  yellow: 'bg-elder-warning hover:bg-amber-600',
  red: 'bg-elder-critical hover:bg-red-700',
  gray: 'bg-gray-400 hover:bg-gray-500',
};

function SensorBadge({ type }: { type: SensorType }) {
  return (
    <div className="flex items-center gap-0.5 bg-black/20 rounded px-0.5 py-px">
      {(type === 'ai-vision' || type === 'hybrid') && (
        <Camera className="h-2.5 w-2.5 opacity-80" />
      )}
      {(type === 'ai-sensor' || type === 'hybrid') && (
        <Radio className="h-2.5 w-2.5 opacity-80" />
      )}
    </div>
  );
}

function ResidentLabel({ name }: { name: string }) {
  return (
    <span className="text-[9px] font-normal opacity-80 truncate max-w-full px-1">
      {name.split(' ')[1] || name}
    </span>
  );
}

export function RoomCard({ room, onClick }: RoomCardProps) {
  const allSensorsOffline = room.sensors.every(s => !s.online);
  const isSemiPrivate = room.roomType === 'semi-private';

  if (isSemiPrivate && room.residents.length === 2) {
    const bedA = room.residents.find(r => r.bedZone === 'A');
    const bedB = room.residents.find(r => r.bedZone === 'B');

    return (
      <button
        onClick={onClick}
        className={cn(
          'relative flex flex-col items-center justify-center rounded-lg text-white font-bold transition-all',
          'w-full aspect-square min-h-[4rem] max-h-[5rem]',
          statusBgMap[room.statusColor],
          room.statusColor === 'red' && 'animate-pulse-critical'
        )}
        aria-label={`Room ${room.number} (semi-private), status: ${room.status}`}
      >
        <span className="text-lg leading-none">{room.number}</span>
        <div className="flex gap-1 mt-0.5 w-full px-1">
          <span className="text-[8px] font-normal opacity-80 truncate flex-1 text-center">
            A: {bedA ? bedA.residentName.split(' ')[1] : '—'}
          </span>
          <span className="text-[8px] opacity-40">|</span>
          <span className="text-[8px] font-normal opacity-80 truncate flex-1 text-center">
            B: {bedB ? bedB.residentName.split(' ')[1] : '—'}
          </span>
        </div>
        <div className="absolute top-1 right-1 flex items-center gap-0.5">
          {allSensorsOffline && <WifiOff className="h-3 w-3 opacity-70" />}
          <SensorBadge type={room.sensorType} />
        </div>
      </button>
    );
  }

  const primaryResident = room.residents[0];

  return (
    <button
      onClick={onClick}
      className={cn(
        'relative flex flex-col items-center justify-center rounded-lg text-white font-bold transition-all',
        'w-full aspect-square min-h-[4rem] max-h-[5rem]',
        statusBgMap[room.statusColor],
        room.statusColor === 'red' && 'animate-pulse-critical'
      )}
      aria-label={`Room ${room.number}, status: ${room.status}`}
    >
      <span className="text-lg leading-none">{room.number}</span>
      {primaryResident && <ResidentLabel name={primaryResident.residentName} />}
      <div className="absolute top-1 right-1 flex items-center gap-0.5">
        {allSensorsOffline && <WifiOff className="h-3 w-3 opacity-70" />}
        <SensorBadge type={room.sensorType} />
      </div>
    </button>
  );
}

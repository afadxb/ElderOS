import type { SensorHealth } from '@/types';
import { TableRow, TableCell } from '@/components/ui';
import { StatusDot, Badge } from '@/components/ui';
import { RelativeTime } from '@/components/common/RelativeTime';
import { cn } from '@/utils/cn';

interface CameraStatusRowProps {
  camera: SensorHealth;
}

const statusColors = { online: 'green' as const, degraded: 'yellow' as const, offline: 'red' as const };

export function CameraStatusRow({ camera }: CameraStatusRowProps) {
  const isHighLatency = camera.inferenceLatencyMs > camera.baselineLatencyMs * 2;

  return (
    <TableRow>
      <TableCell className="font-medium">Room {camera.roomNumber}</TableCell>
      <TableCell>
        <Badge variant="default">{camera.type}</Badge>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1.5">
          <StatusDot color={statusColors[camera.status]} pulse={camera.status === 'offline'} />
          <span className="capitalize">{camera.status}</span>
        </div>
      </TableCell>
      <TableCell><RelativeTime timestamp={camera.lastHeartbeat} /></TableCell>
      <TableCell>
        <span className={cn('font-mono', isHighLatency && 'text-elder-critical font-semibold')}>
          {camera.status === 'offline' ? '—' : `${camera.inferenceLatencyMs}ms`}
        </span>
      </TableCell>
      <TableCell>{camera.uptime.toFixed(1)}%</TableCell>
      <TableCell className="text-elder-text-muted">{camera.firmwareVersion}</TableCell>
    </TableRow>
  );
}

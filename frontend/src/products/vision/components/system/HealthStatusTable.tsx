import type { SensorHealth } from '@/types';
import { Table, TableHeader, TableBody, TableHead, EmptyState } from '@/components/ui';
import { CameraStatusRow } from './CameraStatusRow';
import { Activity } from 'lucide-react';

interface HealthStatusTableProps {
  cameras: SensorHealth[];
}

export function HealthStatusTable({ cameras }: HealthStatusTableProps) {
  if (cameras.length === 0) {
    return <EmptyState icon={<Activity className="h-12 w-12" />} title="No sensors" />;
  }

  return (
    <Table>
      <TableHeader>
        <tr>
          <TableHead>Room</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Last Heartbeat</TableHead>
          <TableHead>Latency</TableHead>
          <TableHead>Uptime</TableHead>
          <TableHead>Firmware</TableHead>
        </tr>
      </TableHeader>
      <TableBody>
        {cameras.map(sensor => (
          <CameraStatusRow key={sensor.sensorId} camera={sensor} />
        ))}
      </TableBody>
    </Table>
  );
}

import type { AlertEvent } from '@/types';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, EmptyState } from '@/components/ui';
import { EVENT_TYPE_LABELS } from '@/constants';
import { RelativeTime } from '@/components/common/RelativeTime';
import { TriageActions } from './TriageActions';
import { ReviewCard } from './ReviewCard';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { ClipboardCheck } from 'lucide-react';

interface ReviewQueueTableProps {
  events: AlertEvent[];
  onConfirm: (eventId: string) => void;
  onDismiss: (eventId: string) => void;
}

export function ReviewQueueTable({ events, onConfirm, onDismiss }: ReviewQueueTableProps) {
  const isMobile = useIsMobile();

  if (events.length === 0) {
    return <EmptyState icon={<ClipboardCheck className="h-12 w-12" />} title="Review queue empty" description="No medium-confidence events awaiting review." />;
  }

  if (isMobile) {
    return (
      <div className="space-y-3">
        {events.map(event => (
          <ReviewCard key={event.id} event={event} onConfirm={onConfirm} onDismiss={onDismiss} />
        ))}
      </div>
    );
  }

  return (
    <Table>
      <TableHeader>
        <tr>
          <TableHead>Time</TableHead>
          <TableHead>Room</TableHead>
          <TableHead>Event Type</TableHead>
          <TableHead>Confidence</TableHead>
          <TableHead>Resident</TableHead>
          <TableHead>Actions</TableHead>
        </tr>
      </TableHeader>
      <TableBody>
        {events.map(event => (
          <TableRow key={event.id}>
            <TableCell><RelativeTime timestamp={event.detectedAt} /></TableCell>
            <TableCell className="font-medium">{event.roomNumber}</TableCell>
            <TableCell>{EVENT_TYPE_LABELS[event.eventType]}</TableCell>
            <TableCell><span className="font-mono">{event.confidenceScore}%</span></TableCell>
            <TableCell>{event.residentName}</TableCell>
            <TableCell><TriageActions onConfirm={() => onConfirm(event.id)} onDismiss={() => onDismiss(event.id)} /></TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

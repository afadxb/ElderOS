import type { AlertEvent } from '@/types';
import { Card, CardContent, Badge } from '@/components/ui';
import { EVENT_TYPE_LABELS } from '@/constants';
import { RelativeTime } from '@/components/common/RelativeTime';
import { TriageActions } from './TriageActions';

interface ReviewCardProps {
  event: AlertEvent;
  onConfirm: (eventId: string) => void;
  onDismiss: (eventId: string) => void;
}

export function ReviewCard({ event, onConfirm, onDismiss }: ReviewCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="flex items-start justify-between mb-2">
          <div>
            <p className="text-sm font-semibold">{EVENT_TYPE_LABELS[event.eventType]} — Room {event.roomNumber}</p>
            <p className="text-xs text-elder-text-secondary">
              {event.residentName}
              {event.bedZone && <span className="ml-1 opacity-70">Bed {event.bedZone}</span>}
            </p>
            <RelativeTime timestamp={event.detectedAt} />
          </div>
          <Badge variant="warning">
            {event.confidenceScore}% confidence
          </Badge>
        </div>
        <p className="text-xs text-elder-text-secondary mb-3">{event.preEventSummary}</p>
        <TriageActions onConfirm={() => onConfirm(event.id)} onDismiss={() => onDismiss(event.id)} />
      </CardContent>
    </Card>
  );
}

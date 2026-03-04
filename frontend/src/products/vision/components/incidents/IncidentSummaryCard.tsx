import type { Incident } from '@/types';
import { Card, CardContent, Badge } from '@/components/ui';
import { ResponseTimeBadge } from './ResponseTimeBadge';
import { EVENT_TYPE_LABELS, RESPONSE_TIME_THRESHOLDS } from '@/constants';
import { alertStatusToBadge } from '@/utils/colorUtils';
import { NTPTimestamp } from '@/components/common/NTPTimestamp';
import { useNavigate } from 'react-router-dom';

interface IncidentSummaryCardProps {
  incident: Incident;
  onClick?: () => void;
}

export function IncidentSummaryCard({ incident, onClick }: IncidentSummaryCardProps) {
  const statusBadge = alertStatusToBadge(incident.status);

  return (
    <Card hover={!!onClick} onClick={onClick} className="cursor-pointer">
      <CardContent>
        <div className="flex items-start justify-between mb-2">
          <div>
            <p className="text-sm font-semibold">{EVENT_TYPE_LABELS[incident.eventType]} — Room {incident.roomNumber}</p>
            <p className="text-xs text-elder-text-secondary">
              {incident.residentName}
              {incident.bedZone && <span className="ml-1 opacity-70">Bed {incident.bedZone}</span>}
            </p>
          </div>
          <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge.className}`}>
            {statusBadge.label}
          </span>
        </div>
        <NTPTimestamp timestamp={incident.ntpTimestamp} />
        <div className="flex items-center gap-2 mt-2">
          <ResponseTimeBadge label="Ack" seconds={incident.ackResponseSeconds} thresholdSeconds={RESPONSE_TIME_THRESHOLDS.ackWarningSeconds} />
          <ResponseTimeBadge label="Resolve" seconds={incident.resolveResponseSeconds} thresholdSeconds={RESPONSE_TIME_THRESHOLDS.resolveWarningSeconds} />
          {incident.isRepeatFall && <Badge variant="critical">Repeat</Badge>}
        </div>
      </CardContent>
    </Card>
  );
}

import { useState } from 'react';
import type { AlertEvent } from '@/types';
import { EVENT_TYPE_LABELS } from '@/constants';
import { cn } from '@/utils/cn';
import { AlertCountdown } from './AlertCountdown';
import { AcknowledgeButton } from './AcknowledgeButton';
import { ResolveButton } from './ResolveButton';
import { DEFAULT_ESCALATION_INTERVALS } from '@/constants';
import { Badge } from '@/components/ui';
import { AlertTriangle, ArrowDown, Camera, Radio, Layers } from 'lucide-react';

interface AlertCardProps {
  event: AlertEvent;
  onAcknowledge: (eventId: string) => void;
  onResolve: (eventId: string) => void;
  compact?: boolean;
}

export function AlertCard({ event, onAcknowledge, onResolve, compact }: AlertCardProps) {
  const [ackLoading, setAckLoading] = useState(false);
  const [resolveLoading, setResolveLoading] = useState(false);
  const isAcknowledged = event.status === 'acknowledged';
  const isCritical = event.severity === 'critical';

  const handleAcknowledge = async () => {
    setAckLoading(true);
    onAcknowledge(event.id);
    setTimeout(() => setAckLoading(false), 300);
  };

  const handleResolve = async () => {
    setResolveLoading(true);
    onResolve(event.id);
    setTimeout(() => setResolveLoading(false), 300);
  };

  if (compact) {
    return (
      <div className={cn(
        'flex items-center justify-between p-3 rounded-lg border-l-4',
        isCritical ? 'bg-elder-critical-bg border-elder-critical' : 'bg-elder-warning-bg border-elder-warning'
      )}>
        <div className="flex items-center gap-3 min-w-0">
          <AlertTriangle className={cn('h-5 w-5 flex-shrink-0', isCritical ? 'text-elder-critical' : 'text-elder-warning')} />
          <div className="min-w-0">
            <p className="text-sm font-semibold truncate">
              {EVENT_TYPE_LABELS[event.eventType]} — Room {event.roomNumber}
            </p>
            <p className="text-xs text-elder-text-secondary truncate">
              {event.residentName}
              {event.bedZone && <span className="ml-1 opacity-70">Bed {event.bedZone}</span>}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          {event.sensorSource === 'ai-sensor' && <span aria-label="AI Sensor detection"><Radio className="h-3.5 w-3.5 text-elder-text-muted" /></span>}
          {event.sensorSource === 'fused' && <span aria-label="Fused detection"><Layers className="h-3.5 w-3.5 text-elder-text-muted" /></span>}
          {event.isRepeatFall && <Badge variant="critical">Repeat</Badge>}
          {!isAcknowledged ? (
            <button
              onClick={handleAcknowledge}
              className="px-3 py-1.5 text-xs font-semibold text-white bg-elder-action rounded-md hover:bg-blue-700"
            >
              ACK
            </button>
          ) : (
            <button
              onClick={handleResolve}
              className="px-3 py-1.5 text-xs font-semibold text-elder-action border border-elder-action rounded-md hover:bg-elder-action-bg"
            >
              Resolve
            </button>
          )}
        </div>
      </div>
    );
  }

  // Full-screen alert card (PSW mobile view)
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-between min-h-[80vh] p-6 rounded-xl',
        isCritical ? 'bg-elder-critical-bg' : 'bg-elder-warning-bg'
      )}
      role="alert"
      aria-live="assertive"
    >
      <div className="text-center space-y-1 pt-4">
        <p className={cn(
          'text-sm font-bold uppercase tracking-widest',
          isCritical ? 'text-elder-critical' : 'text-elder-warning'
        )}>
          {EVENT_TYPE_LABELS[event.eventType]}
        </p>
        {event.isRepeatFall && (
          <Badge variant="critical" dot pulse>Repeat Fall</Badge>
        )}
      </div>

      <div className="text-center space-y-2">
        <p className="text-room-number text-elder-text-primary">
          Room {event.roomNumber}
          {event.bedZone && <span className="text-2xl ml-2 font-normal opacity-60">Bed {event.bedZone}</span>}
        </p>
        <p className="text-lg text-elder-text-secondary">{event.residentName}</p>
        <div className="flex items-center justify-center gap-3 text-sm text-elder-text-muted">
          <span>Confidence: {event.confidenceScore}%</span>
          <span className="flex items-center gap-1">
            {event.sensorSource === 'ai-vision' && <Camera className="h-3.5 w-3.5" />}
            {event.sensorSource === 'ai-sensor' && <Radio className="h-3.5 w-3.5" />}
            {event.sensorSource === 'fused' && <Layers className="h-3.5 w-3.5" />}
            {event.sensorSource}
          </span>
        </div>
      </div>

      <AlertCountdown
        detectedAt={event.detectedAt}
        escalationThresholdSeconds={DEFAULT_ESCALATION_INTERVALS.level1Seconds}
        isAcknowledged={isAcknowledged}
      />

      <div className="w-full max-w-sm space-y-3 pb-4">
        {!isAcknowledged ? (
          <AcknowledgeButton onAcknowledge={handleAcknowledge} loading={ackLoading} />
        ) : (
          <>
            <ResolveButton onResolve={handleResolve} loading={resolveLoading} />
            <p className="text-xs text-center text-elder-text-muted">
              Acknowledged — attend to resident and mark resolved
            </p>
          </>
        )}
      </div>
    </div>
  );
}

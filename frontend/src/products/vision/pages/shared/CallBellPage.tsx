import { useState, useEffect } from 'react';
import { Card, CardContent, Spinner, Badge, Button } from '@/components/ui';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { UnitSelector } from '@/components/common/UnitSelector';
import { RelativeTime } from '@/components/common/RelativeTime';
import { CallBellPriorityBadge } from '@/components/callbell/CallBellPriorityBadge';
import { CALL_BELL_ORIGIN_LABELS, CALL_BELL_STATUS_LABELS, CALL_BELL_THRESHOLDS } from '@/constants/callBell';
import { usePagination } from '@/hooks/usePagination';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { formatResponseTime } from '@/utils/formatters';
import * as callBellService from '@/services/callBellService';
import type { CallBellEvent } from '@/types';

const STATUS_BADGE_STYLES: Record<string, string> = {
  active: 'bg-red-100 text-red-800',
  responded: 'bg-amber-100 text-amber-800',
  closed: 'bg-green-100 text-green-800',
  cancelled: 'bg-gray-100 text-gray-700',
};

function ResponseTimeCell({ seconds }: { seconds: number | null }) {
  if (seconds === null) return <span className="text-elder-text-muted">--</span>;
  const color =
    seconds <= CALL_BELL_THRESHOLDS.responseGoodSeconds
      ? 'text-green-700'
      : seconds <= CALL_BELL_THRESHOLDS.responseWarningSeconds
        ? 'text-amber-700'
        : 'text-red-700';
  return <span className={`font-mono ${color}`}>{formatResponseTime(seconds)}</span>;
}

export function CallBellPage() {
  const isMobile = useIsMobile();
  const [events, setEvents] = useState<CallBellEvent[]>([]);
  const [unit, setUnit] = useState('');
  const [shift, setShift] = useState('');
  const [priority, setPriority] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const result = await callBellService.getCallBellEvents({
        unit: unit || undefined,
        shift: shift || undefined,
        priority: priority || undefined,
        pageSize: 500,
      });
      setEvents(result.data);
      setLoading(false);
    }
    load();
  }, [unit, shift, priority]);

  const { paginatedItems, page, totalPages, nextPage, prevPage, hasNext, hasPrev } = usePagination(events, 20);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Call Bell"
        subtitle="Nurse call system events"
        actions={
          <div className="flex items-center gap-2 flex-wrap">
            <UnitSelector value={unit} onChange={setUnit} />
            <select
              value={shift}
              onChange={e => setShift(e.target.value)}
              className="text-sm border border-elder-border rounded-md px-2 py-1.5 bg-white"
            >
              <option value="">All Shifts</option>
              <option value="Day">Day</option>
              <option value="Evening">Evening</option>
              <option value="Night">Night</option>
            </select>
            <select
              value={priority}
              onChange={e => setPriority(e.target.value)}
              className="text-sm border border-elder-border rounded-md px-2 py-1.5 bg-white"
            >
              <option value="">All Priority</option>
              <option value="emergency">Emergency</option>
              <option value="urgent">Urgent</option>
              <option value="normal">Normal</option>
            </select>
          </div>
        }
      />

      {isMobile ? (
        <div className="space-y-3">
          {paginatedItems.map(evt => (
            <Card key={evt.id}>
              <CardContent>
                <div className="flex items-start justify-between mb-1">
                  <div>
                    <span className="font-bold text-lg">Room {evt.roomNumber}</span>
                    <span className="text-xs text-elder-text-muted ml-2">{evt.residentName}</span>
                  </div>
                  <CallBellPriorityBadge priority={evt.priority} />
                </div>
                <div className="flex items-center gap-3 text-sm text-elder-text-secondary">
                  <span>{CALL_BELL_ORIGIN_LABELS[evt.origin]}</span>
                  <span>·</span>
                  <RelativeTime timestamp={evt.pressedAt} />
                </div>
                <div className="flex items-center justify-between mt-2">
                  <ResponseTimeCell seconds={evt.responseTimeSeconds} />
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE_STYLES[evt.status]}`}>
                    {CALL_BELL_STATUS_LABELS[evt.status]}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card padding="none">
          <Table>
            <TableHeader>
              <tr>
                <TableHead>Time</TableHead>
                <TableHead>Room</TableHead>
                <TableHead>Resident</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Origin</TableHead>
                <TableHead>Response Time</TableHead>
                <TableHead>Responded By</TableHead>
                <TableHead>Status</TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {paginatedItems.map(evt => (
                <TableRow key={evt.id}>
                  <TableCell><RelativeTime timestamp={evt.pressedAt} /></TableCell>
                  <TableCell className="font-medium">{evt.roomNumber}</TableCell>
                  <TableCell>{evt.residentName}</TableCell>
                  <TableCell><CallBellPriorityBadge priority={evt.priority} /></TableCell>
                  <TableCell>{CALL_BELL_ORIGIN_LABELS[evt.origin]}</TableCell>
                  <TableCell><ResponseTimeCell seconds={evt.responseTimeSeconds} /></TableCell>
                  <TableCell>{evt.respondedByName || '--'}</TableCell>
                  <TableCell>
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE_STYLES[evt.status]}`}>
                      {CALL_BELL_STATUS_LABELS[evt.status]}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-elder-text-secondary">Page {page} of {totalPages} ({events.length} events)</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={prevPage} disabled={!hasPrev}>Previous</Button>
            <Button variant="outline" size="sm" onClick={nextPage} disabled={!hasNext}>Next</Button>
          </div>
        </div>
      )}
    </div>
  );
}

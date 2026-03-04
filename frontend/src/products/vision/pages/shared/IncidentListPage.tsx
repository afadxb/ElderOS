import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Spinner, Badge } from '@/components/ui';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { UnitSelector } from '@/components/common/UnitSelector';
import { RelativeTime } from '@/components/common/RelativeTime';
import { ResponseTimeBadge } from '@/components/incidents/ResponseTimeBadge';
import { alertStatusToBadge } from '@/utils/colorUtils';
import { EVENT_TYPE_LABELS, RESPONSE_TIME_THRESHOLDS } from '@/constants';
import { usePagination } from '@/hooks/usePagination';
import { useIsMobile } from '@/hooks/useMediaQuery';
import { IncidentSummaryCard } from '@/components/incidents/IncidentSummaryCard';
import { Button } from '@/components/ui';
import * as incidentService from '@/services/incidentService';
import type { Incident } from '@/types';

export function IncidentListPage() {
  const navigate = useNavigate();
  const isMobile = useIsMobile();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [unit, setUnit] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const result = await incidentService.getIncidents({ unit: unit || undefined, pageSize: 100 });
      setIncidents(result.data);
      setLoading(false);
    }
    load();
  }, [unit]);

  const { paginatedItems, page, totalPages, nextPage, prevPage, hasNext, hasPrev } = usePagination(incidents, 15);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader title="Incidents" subtitle="All recorded safety events" actions={<UnitSelector value={unit} onChange={setUnit} />} />

      {isMobile ? (
        <div className="space-y-3">
          {paginatedItems.map(inc => (
            <IncidentSummaryCard key={inc.id} incident={inc} onClick={() => navigate(`/vision/incidents/${inc.id}`)} />
          ))}
        </div>
      ) : (
        <Card padding="none">
          <Table>
            <TableHeader>
              <tr>
                <TableHead>Time</TableHead>
                <TableHead>Room</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Resident</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Ack Time</TableHead>
                <TableHead>Status</TableHead>
              </tr>
            </TableHeader>
            <TableBody>
              {paginatedItems.map(inc => {
                const statusBadge = alertStatusToBadge(inc.status);
                return (
                  <TableRow key={inc.id} onClick={() => navigate(`/vision/incidents/${inc.id}`)}>
                    <TableCell><RelativeTime timestamp={inc.detectedAt} /></TableCell>
                    <TableCell className="font-medium">{inc.roomNumber}</TableCell>
                    <TableCell>{EVENT_TYPE_LABELS[inc.eventType]}</TableCell>
                    <TableCell>{inc.residentName}</TableCell>
                    <TableCell><span className="font-mono">{inc.confidenceScore}%</span></TableCell>
                    <TableCell>
                      <ResponseTimeBadge label="Ack" seconds={inc.ackResponseSeconds} thresholdSeconds={RESPONSE_TIME_THRESHOLDS.ackWarningSeconds} />
                    </TableCell>
                    <TableCell>
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge.className}`}>{statusBadge.label}</span>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Card>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-elder-text-secondary">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={prevPage} disabled={!hasPrev}>Previous</Button>
            <Button variant="outline" size="sm" onClick={nextPage} disabled={!hasNext}>Next</Button>
          </div>
        </div>
      )}
    </div>
  );
}

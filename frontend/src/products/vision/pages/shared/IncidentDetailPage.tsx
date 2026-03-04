import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, Badge, Spinner, Button } from '@/components/ui';
import { IncidentTimeline } from '@/components/incidents/IncidentTimeline';
import { ResponseTimeBadge } from '@/components/incidents/ResponseTimeBadge';
import { EscalationTimeline } from '@/components/incidents/EscalationTimeline';
import { PDFExportButton } from '@/components/export/PDFExportButton';
import { PageHeader } from '@/components/common/PageHeader';
import { NTPTimestamp } from '@/components/common/NTPTimestamp';
import { alertStatusToBadge } from '@/utils/colorUtils';
import { EVENT_TYPE_LABELS, RESPONSE_TIME_THRESHOLDS } from '@/constants';
import * as incidentService from '@/services/incidentService';
import type { Incident } from '@/types';
import { ArrowLeft } from 'lucide-react';

export function IncidentDetailPage() {
  const { incidentId } = useParams<{ incidentId: string }>();
  const navigate = useNavigate();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!incidentId) return;
      const data = await incidentService.getIncidentById(incidentId);
      setIncident(data || null);
      setLoading(false);
    }
    load();
  }, [incidentId]);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  if (!incident) return <div className="text-center py-12"><p>Incident not found</p></div>;

  const statusBadge = alertStatusToBadge(incident.status);

  const timelineSteps = [
    { timestamp: incident.detectedAt, label: `${EVENT_TYPE_LABELS[incident.eventType]} detected`, type: 'detection' as const },
    ...(incident.acknowledgedAt ? [{ timestamp: incident.acknowledgedAt, label: `Acknowledged by ${incident.acknowledgedBy || 'staff'}`, type: 'acknowledgment' as const }] : []),
    ...incident.escalationTimeline.map(e => ({ timestamp: e.triggeredAt, label: e.action, type: 'escalation' as const })),
    ...(incident.resolvedAt ? [{ timestamp: incident.resolvedAt, label: `Resolved by ${incident.resolvedBy || 'staff'}`, type: 'resolution' as const }] : []),
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <PageHeader
        title={`Incident — Room ${incident.roomNumber}`}
        actions={
          <div className="flex items-center gap-2">
            <PDFExportButton type="incident" id={incident.id} />
            <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Event Summary</CardTitle>
              <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusBadge.className}`}>{statusBadge.label}</span>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                <div><span className="text-elder-text-secondary">Event Type</span><p className="font-medium">{EVENT_TYPE_LABELS[incident.eventType]}</p></div>
                <div><span className="text-elder-text-secondary">Resident</span><p className="font-medium">{incident.residentName}{incident.bedZone && ` (Bed ${incident.bedZone})`}</p></div>
                <div><span className="text-elder-text-secondary">Confidence</span><p className="font-medium">{incident.confidenceScore}% ({incident.confidence})</p></div>
                <div><span className="text-elder-text-secondary">NTP Timestamp</span><NTPTimestamp timestamp={incident.ntpTimestamp} /></div>
              </div>
              {incident.isRepeatFall && <Badge variant="critical" className="mb-3">Repeat Fall</Badge>}
              <div className="flex items-center gap-2 mt-3">
                <ResponseTimeBadge label="Ack" seconds={incident.ackResponseSeconds} thresholdSeconds={RESPONSE_TIME_THRESHOLDS.ackWarningSeconds} />
                <ResponseTimeBadge label="Resolve" seconds={incident.resolveResponseSeconds} thresholdSeconds={RESPONSE_TIME_THRESHOLDS.resolveWarningSeconds} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Pre-Event Summary</CardTitle></CardHeader>
            <CardContent><p className="text-sm text-elder-text-secondary">{incident.preEventSummary}</p></CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Post-Event State</CardTitle></CardHeader>
            <CardContent><p className="text-sm text-elder-text-secondary">{incident.postEventState}</p></CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Event Timeline</CardTitle></CardHeader>
            <CardContent><IncidentTimeline steps={timelineSteps} /></CardContent>
          </Card>
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Escalation</CardTitle></CardHeader>
            <CardContent><EscalationTimeline steps={incident.escalationTimeline} /></CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Notes</CardTitle></CardHeader>
            <CardContent>
              <p className="text-sm text-elder-text-muted">{incident.notes || 'No notes added.'}</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

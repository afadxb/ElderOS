import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAlerts } from '@/hooks/useAlerts';
import { Card, CardHeader, CardTitle, CardContent, Spinner, Button } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { AlertTimeline } from '@/components/charts/AlertTimeline';
import { ResponseTimeChart } from '@/components/charts/ResponseTimeChart';
import { AlertStack } from '@/components/alerts/AlertStack';
import { RoomStatusGrid } from '@/components/rooms/RoomStatusGrid';
import { RiskScoreCard } from '@/components/residents/RiskScoreCard';
import { PDFExportButton } from '@/components/export/PDFExportButton';
import { getCurrentShift } from '@/utils/dateUtils';
import { formatResponseTime } from '@/utils/formatters';
import { generateResponseTimeDistribution } from '@/mock/generators/responseTimeData';
import * as roomService from '@/services/roomService';
import * as residentService from '@/services/residentService';
import * as alertService from '@/services/alertService';
import type { Room, Resident, AlertEvent } from '@/types';

export function SupervisorDashboard() {
  const navigate = useNavigate();
  const { activeAlerts, unacknowledgedCount, acknowledge, resolve } = useAlerts();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [highRisk, setHighRisk] = useState<Resident[]>([]);
  const [recentEvents, setRecentEvents] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [r, hr, events] = await Promise.all([
        roomService.getRooms(),
        residentService.getHighRiskResidents(),
        alertService.getRecentEvents(60),
      ]);
      setRooms(r);
      setHighRisk(hr);
      setRecentEvents(events);
      setLoading(false);
    }
    load();
  }, []);

  const responseData = generateResponseTimeDistribution();
  const currentShift = getCurrentShift();
  const escalatedCount = activeAlerts.filter(a => a.escalationLevel > 0).length;
  const avgAck = recentEvents.filter(e => e.acknowledgedAt).length > 0
    ? Math.round(recentEvents.filter(e => e.acknowledgedAt).reduce((sum, e) => {
        const ack = new Date(e.acknowledgedAt!).getTime() - new Date(e.detectedAt).getTime();
        return sum + ack / 1000;
      }, 0) / recentEvents.filter(e => e.acknowledgedAt).length)
    : 0;

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Supervisor Dashboard"
        subtitle={`${currentShift} Shift Overview`}
        actions={<PDFExportButton type="shift-summary" id="today" label="Export Shift Report" />}
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Events (60 min)</p>
            <p className="text-2xl font-bold">{recentEvents.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Unacknowledged</p>
            <p className="text-2xl font-bold text-elder-critical">{unacknowledgedCount}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Avg Ack Time</p>
            <p className="text-2xl font-bold">{formatResponseTime(avgAck)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Escalated</p>
            <p className="text-2xl font-bold text-elder-warning">{escalatedCount}</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Alert Timeline (60 min)</CardTitle></CardHeader>
          <CardContent><AlertTimeline events={recentEvents} /></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Response Time Distribution</CardTitle></CardHeader>
          <CardContent><ResponseTimeChart data={responseData} /></CardContent>
        </Card>
      </div>

      {/* Alerts + Review */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Active Alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <AlertStack alerts={activeAlerts.slice(0, 5)} onAcknowledge={acknowledge} onResolve={resolve} />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Review Queue</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate('/vision/review')}>View All</Button>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-elder-text-secondary">
              {activeAlerts.filter(a => a.confidence === 'medium').length} events awaiting review
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Room Grid + High Risk */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Room Grid</CardTitle></CardHeader>
          <CardContent><RoomStatusGrid rooms={rooms} compact /></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>High Risk Residents</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-2">
              {highRisk.slice(0, 5).map(r => (
                <RiskScoreCard key={r.id} resident={r} />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

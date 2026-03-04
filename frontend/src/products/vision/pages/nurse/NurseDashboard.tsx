import { useState, useEffect } from 'react';
import { useAlerts } from '@/hooks/useAlerts';
import { AlertCard } from '@/components/alerts/AlertCard';
import { AlertBanner } from '@/components/alerts/AlertBanner';
import { AlertStack } from '@/components/alerts/AlertStack';
import { RoomStatusGrid } from '@/components/rooms/RoomStatusGrid';
import { RiskScoreCard } from '@/components/residents/RiskScoreCard';
import { Card, CardHeader, CardTitle, CardContent, Spinner } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import * as roomService from '@/services/roomService';
import * as residentService from '@/services/residentService';
import type { Room, Resident } from '@/types';

export function NurseDashboard() {
  const { activeAlerts, criticalAlerts, unacknowledgedCount, acknowledge, resolve } = useAlerts();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [highRiskResidents, setHighRiskResidents] = useState<Resident[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [r, hr] = await Promise.all([
        roomService.getRooms(),
        residentService.getHighRiskResidents(),
      ]);
      setRooms(r);
      setHighRiskResidents(hr);
      setLoading(false);
    }
    load();
  }, []);

  // Full-screen takeover for critical unacknowledged alerts
  const topCritical = criticalAlerts.find(a => a.status === 'active');
  if (topCritical) {
    return (
      <div className="max-w-lg mx-auto">
        <AlertCard event={topCritical} onAcknowledge={acknowledge} onResolve={resolve} />
        {activeAlerts.length > 1 && (
          <p className="text-center text-sm text-elder-text-muted mt-3">
            {activeAlerts.length - 1} more alert{activeAlerts.length - 1 !== 1 ? 's' : ''} pending
          </p>
        )}
      </div>
    );
  }

  if (loading) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <AlertBanner count={unacknowledgedCount} criticalCount={criticalAlerts.filter(a => a.status === 'active').length} />

      <section>
        <CardHeader><CardTitle>Active Alerts</CardTitle></CardHeader>
        <AlertStack alerts={activeAlerts} onAcknowledge={acknowledge} onResolve={resolve} />
      </section>

      <section>
        <Card>
          <CardHeader><CardTitle>Room Grid</CardTitle></CardHeader>
          <CardContent>
            <RoomStatusGrid rooms={rooms} compact />
          </CardContent>
        </Card>
      </section>

      {highRiskResidents.length > 0 && (
        <section>
          <CardHeader><CardTitle>High Risk Residents</CardTitle></CardHeader>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {highRiskResidents.slice(0, 6).map(resident => (
              <RiskScoreCard key={resident.id} resident={resident} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

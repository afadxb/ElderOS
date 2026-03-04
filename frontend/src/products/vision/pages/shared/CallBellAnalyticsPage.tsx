import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Spinner } from '@/components/ui';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';
import { Tabs, TabPanel } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { UnitSelector } from '@/components/common/UnitSelector';
import { StaffResponseChart } from '@/components/callbell/StaffResponseChart';
import { CallBellShiftChart } from '@/components/callbell/CallBellShiftChart';
import { CallBellTrendChart } from '@/components/callbell/CallBellTrendChart';
import { formatResponseTime } from '@/utils/formatters';
import { CALL_BELL_THRESHOLDS } from '@/constants/callBell';
import * as callBellService from '@/services/callBellService';
import type { CallBellStaffMetrics, CallBellFloorMetrics, CallBellShiftMetrics, CallBellDailySummary } from '@/types';

const TABS = [
  { id: 'staff', label: 'By Staff' },
  { id: 'floor', label: 'By Floor' },
  { id: 'shift', label: 'By Shift' },
];

export function CallBellAnalyticsPage() {
  const [unit, setUnit] = useState('');
  const [tab, setTab] = useState('staff');
  const [loading, setLoading] = useState(true);
  const [staffMetrics, setStaffMetrics] = useState<CallBellStaffMetrics[]>([]);
  const [floorMetrics, setFloorMetrics] = useState<CallBellFloorMetrics[]>([]);
  const [shiftMetrics, setShiftMetrics] = useState<CallBellShiftMetrics[]>([]);
  const [dailySummaries, setDailySummaries] = useState<CallBellDailySummary[]>([]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const filters = { unit: unit || undefined };
      const [staff, floors, shifts, daily] = await Promise.all([
        callBellService.getStaffMetrics(filters),
        callBellService.getFloorMetrics(),
        callBellService.getShiftMetrics(filters),
        callBellService.getDailySummaries(filters),
      ]);
      setStaffMetrics(staff);
      setFloorMetrics(floors);
      setShiftMetrics(shifts);
      setDailySummaries(daily);
      setLoading(false);
    }
    load();
  }, [unit]);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  // KPI calculations
  const totalCalls = dailySummaries.reduce((s, d) => s + d.totalCalls, 0);
  const avgResponse = dailySummaries.length > 0
    ? Math.round(dailySummaries.reduce((s, d) => s + d.avgResponseSeconds * d.totalCalls, 0) / totalCalls)
    : 0;
  const allResponseTimes = staffMetrics.reduce((s, m) => s + m.callsUnder120s, 0);
  const allCalls = staffMetrics.reduce((s, m) => s + m.totalCalls, 0);
  const complianceRate = allCalls > 0 ? Math.round((allResponseTimes / allCalls) * 100) : 0;
  const emergencyCalls = shiftMetrics.reduce((s, m) => {
    // Count from the raw data - shift metrics don't track emergency directly but we can approximate
    return s;
  }, 0);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Call Bell Analytics"
        subtitle="Response time performance"
        actions={<UnitSelector value={unit} onChange={setUnit} />}
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Total Calls (30d)</p>
            <p className="text-2xl font-bold">{totalCalls.toLocaleString()}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Avg Response Time</p>
            <p className="text-2xl font-bold">{formatResponseTime(avgResponse)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Under 2min Rate</p>
            <p className={`text-2xl font-bold ${complianceRate >= CALL_BELL_THRESHOLDS.complianceTargetPercent ? 'text-elder-ok' : 'text-elder-warning'}`}>
              {complianceRate}%
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Staff Tracked</p>
            <p className="text-2xl font-bold">{staffMetrics.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs tabs={TABS} activeTab={tab} onChange={setTab} />

      {/* By Staff */}
      <TabPanel id="staff" activeTab={tab}>
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Avg Response Time by Staff</CardTitle></CardHeader>
            <CardContent>
              <StaffResponseChart data={staffMetrics} />
            </CardContent>
          </Card>
          <Card padding="none">
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Staff</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Calls</TableHead>
                  <TableHead>Avg</TableHead>
                  <TableHead>Median</TableHead>
                  <TableHead>&lt;60s</TableHead>
                  <TableHead>&gt;3m</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {staffMetrics.map(m => (
                  <TableRow key={m.staffId}>
                    <TableCell className="font-medium">{m.staffName}</TableCell>
                    <TableCell>{m.role}</TableCell>
                    <TableCell>{m.totalCalls}</TableCell>
                    <TableCell className="font-mono">{formatResponseTime(m.avgResponseSeconds)}</TableCell>
                    <TableCell className="font-mono">{formatResponseTime(m.medianResponseSeconds)}</TableCell>
                    <TableCell className="text-green-700">{m.callsUnder60s}</TableCell>
                    <TableCell className="text-red-700">{m.callsOver180s}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>
      </TabPanel>

      {/* By Floor */}
      <TabPanel id="floor" activeTab={tab}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {floorMetrics.map(m => (
            <Card key={`${m.floor}-${m.unit}`}>
              <CardHeader>
                <CardTitle>{m.unit} (Floor {m.floor})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-elder-text-secondary">Total Calls</p>
                    <p className="text-xl font-bold">{m.totalCalls}</p>
                  </div>
                  <div>
                    <p className="text-elder-text-secondary">Avg Response</p>
                    <p className="text-xl font-bold font-mono">{formatResponseTime(m.avgResponseSeconds)}</p>
                  </div>
                  <div>
                    <p className="text-elder-text-secondary">Peak Hour</p>
                    <p className="font-medium">{m.peakHour}:00</p>
                  </div>
                  <div>
                    <p className="text-elder-text-secondary">Top Origin</p>
                    <p className="font-medium">
                      {Object.entries(m.callsByOrigin).sort(([, a], [, b]) => b - a)[0]?.[0] || '--'}
                    </p>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-elder-border">
                  <p className="text-xs text-elder-text-secondary mb-1">By Priority</p>
                  <div className="flex gap-3 text-xs">
                    <span className="text-red-700">Emergency: {m.callsByPriority.emergency}</span>
                    <span className="text-amber-700">Urgent: {m.callsByPriority.urgent}</span>
                    <span className="text-blue-700">Normal: {m.callsByPriority.normal}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </TabPanel>

      {/* By Shift */}
      <TabPanel id="shift" activeTab={tab}>
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle>Calls & Slow Responses by Shift</CardTitle></CardHeader>
            <CardContent>
              <CallBellShiftChart data={shiftMetrics} />
            </CardContent>
          </Card>
          <Card padding="none">
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Shift</TableHead>
                  <TableHead>Total Calls</TableHead>
                  <TableHead>Avg Response</TableHead>
                  <TableHead>&lt;60s</TableHead>
                  <TableHead>&lt;2m</TableHead>
                  <TableHead>Slow (&gt;3m)</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {shiftMetrics.map(m => (
                  <TableRow key={m.shift}>
                    <TableCell className="font-medium">{m.shift}</TableCell>
                    <TableCell>{m.totalCalls}</TableCell>
                    <TableCell className="font-mono">{formatResponseTime(m.avgResponseSeconds)}</TableCell>
                    <TableCell className="text-green-700">{m.respondedWithin60s}</TableCell>
                    <TableCell>{m.respondedWithin120s}</TableCell>
                    <TableCell className="text-red-700">{m.slowResponses}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </div>
      </TabPanel>

      {/* 30-Day Trend (always visible) */}
      <Card>
        <CardHeader><CardTitle>30-Day Trend</CardTitle></CardHeader>
        <CardContent>
          <CallBellTrendChart data={dailySummaries} />
        </CardContent>
      </Card>
    </div>
  );
}

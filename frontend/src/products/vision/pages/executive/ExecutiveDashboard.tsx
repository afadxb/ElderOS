import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent, Spinner, Button } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { FallsTrendChart } from '@/components/charts/FallsTrendChart';
import { UnitComparisonChart } from '@/components/charts/UnitComparisonChart';
import { ShiftComparisonChart } from '@/components/charts/ShiftComparisonChart';
import { formatResponseTime } from '@/utils/formatters';
import * as reportService from '@/services/reportService';
import type { BoardReportData, ShiftSummary } from '@/types';

export function ExecutiveDashboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<BoardReportData | null>(null);
  const [shiftSummaries, setShiftSummaries] = useState<ShiftSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [boardData, shifts] = await Promise.all([
        reportService.getBoardReportData(),
        reportService.getShiftSummaries(),
      ]);
      setData(boardData);
      setShiftSummaries(shifts);
      setLoading(false);
    }
    load();
  }, []);

  if (loading || !data) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  const totalFalls = data.unitSummaries.reduce((s, u) => s + u.falls, 0);
  const avgResponse = Math.round(data.unitSummaries.reduce((s, u) => s + u.avgResponseTime, 0) / data.unitSummaries.length);
  const avgUnwitnessed = Math.round(data.unitSummaries.reduce((s, u) => s + u.unwitnessedRate, 0) / data.unitSummaries.length);
  const avgCompliance = Math.round(data.unitSummaries.reduce((s, u) => s + u.complianceScore, 0) / data.unitSummaries.length);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Executive Dashboard"
        subtitle={data.facilityName}
        actions={
          <Button variant="primary" size="sm" onClick={() => navigate('/vision/board-report')}>
            Board Report
          </Button>
        }
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Falls (12 Months)</p>
            <p className="text-2xl font-bold text-elder-critical">{totalFalls}</p>
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
            <p className="text-xs text-elder-text-secondary">Unwitnessed Fall Rate</p>
            <p className="text-2xl font-bold text-elder-warning">{avgUnwitnessed}%</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <p className="text-xs text-elder-text-secondary">Compliance Score</p>
            <p className="text-2xl font-bold text-elder-ok">{avgCompliance}%</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Falls & Response Trends (12 Months)</CardTitle></CardHeader>
          <CardContent><FallsTrendChart data={data.trendsMonthly} /></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Unit Comparison</CardTitle></CardHeader>
          <CardContent><UnitComparisonChart data={data.unitSummaries} /></CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <CardHeader><CardTitle>Shift Comparison</CardTitle></CardHeader>
          <CardContent><ShiftComparisonChart summaries={shiftSummaries} /></CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>Liability Indicators</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-elder-text-secondary">Slow Responses (&gt;3 min ack)</span>
                <span className="text-lg font-bold text-elder-critical">{data.liabilityIndicators.slowResponses}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-elder-text-secondary">Unacknowledged Alerts</span>
                <span className="text-lg font-bold text-elder-critical">{data.liabilityIndicators.unacknowledgedAlerts}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-elder-text-secondary">Repeat Falls</span>
                <span className="text-lg font-bold text-elder-warning">{data.liabilityIndicators.repeatFalls}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

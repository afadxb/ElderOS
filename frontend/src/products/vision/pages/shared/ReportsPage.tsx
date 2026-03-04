import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Tabs, TabPanel, Spinner } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { UnitSelector } from '@/components/common/UnitSelector';
import { FallsTrendChart } from '@/components/charts/FallsTrendChart';
import { ResponseTimeChart } from '@/components/charts/ResponseTimeChart';
import { formatResponseTime } from '@/utils/formatters';
import * as reportService from '@/services/reportService';
import { generateResponseTimeDistribution, generateMonthlyTrends } from '@/mock/generators/responseTimeData';
import type { WeeklyDigest } from '@/types';

export function ReportsPage() {
  const [tab, setTab] = useState('weekly');
  const [unit, setUnit] = useState('');
  const [digest, setDigest] = useState<WeeklyDigest | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const d = await reportService.getWeeklyDigest(unit || undefined);
      setDigest(d);
      setLoading(false);
    }
    load();
  }, [unit]);

  const responseData = generateResponseTimeDistribution();
  const trends = generateMonthlyTrends();

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader title="Reports" actions={<UnitSelector value={unit} onChange={setUnit} />} />

      <Tabs
        tabs={[
          { id: 'weekly', label: 'Weekly Digest' },
          { id: 'trends', label: 'Trends' },
          { id: 'response', label: 'Response Times' },
        ]}
        activeTab={tab}
        onChange={setTab}
      />

      <TabPanel id="weekly" activeTab={tab}>
        {digest && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent>
                <p className="text-xs text-elder-text-secondary">Total Falls</p>
                <p className="text-2xl font-bold text-elder-critical">{digest.totalFalls}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <p className="text-xs text-elder-text-secondary">Avg Response</p>
                <p className="text-2xl font-bold">{formatResponseTime(digest.avgResponseTimeSeconds)}</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <p className="text-xs text-elder-text-secondary">Compliance</p>
                <p className="text-2xl font-bold text-elder-ok">{digest.complianceScore}%</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <p className="text-xs text-elder-text-secondary">Trend</p>
                <p className="text-2xl font-bold capitalize">{digest.trendVsPriorWeek}</p>
              </CardContent>
            </Card>
          </div>
        )}
      </TabPanel>

      <TabPanel id="trends" activeTab={tab}>
        <Card>
          <CardHeader><CardTitle>Falls & Response Time (12 Months)</CardTitle></CardHeader>
          <CardContent>
            <FallsTrendChart data={trends} />
          </CardContent>
        </Card>
      </TabPanel>

      <TabPanel id="response" activeTab={tab}>
        <Card>
          <CardHeader><CardTitle>Acknowledgment Time Distribution</CardTitle></CardHeader>
          <CardContent>
            <ResponseTimeChart data={responseData} />
          </CardContent>
        </Card>
      </TabPanel>
    </div>
  );
}

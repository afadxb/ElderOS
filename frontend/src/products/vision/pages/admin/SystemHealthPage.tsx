import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Spinner, Badge } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { HealthStatusTable } from '@/components/system/HealthStatusTable';
import { MetricGauge } from '@/components/system/MetricGauge';
import { NTPDriftIndicator } from '@/components/system/NTPDriftIndicator';
import * as systemService from '@/services/systemService';
import type { SensorHealth, SystemMetrics } from '@/types';
import { CheckCircle, XCircle } from 'lucide-react';

export function SystemHealthPage() {
  const [cameras, setCameras] = useState<SensorHealth[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [selfTest, setSelfTest] = useState<{ passed: boolean; details: string[] } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const [c, m, st] = await Promise.all([
        systemService.getCameraHealth(),
        systemService.getSystemMetrics(),
        systemService.getSelfTestReport(),
      ]);
      setCameras(c);
      setMetrics(m);
      setSelfTest(st);
      setLoading(false);
    }
    load();
  }, []);

  if (loading || !metrics) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  const onlineCount = cameras.filter(c => c.status === 'online').length;
  const degradedCount = cameras.filter(c => c.status === 'degraded').length;
  const offlineCount = cameras.filter(c => c.status === 'offline').length;

  return (
    <div className="space-y-6">
      <PageHeader title="System Health" subtitle="Edge appliance and sensor monitoring" />

      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent><MetricGauge label="CPU" value={metrics.cpuUsage} max={100} /></CardContent>
        </Card>
        <Card>
          <CardContent><MetricGauge label="Memory" value={metrics.memoryUsage} max={100} /></CardContent>
        </Card>
        <Card>
          <CardContent>
            <MetricGauge label="Disk" value={metrics.diskUsagePercent} max={100} warningThreshold={80} criticalThreshold={90} />
            <p className="text-xs text-elder-text-muted mt-1">{metrics.diskUsedGB.toFixed(0)} GB / {metrics.diskTotalGB} GB</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <NTPDriftIndicator metrics={metrics} />
            <p className="text-xs text-elder-text-muted mt-2">Uptime: {metrics.edgeDeviceUptime}</p>
          </CardContent>
        </Card>
      </div>

      {/* Camera Summary */}
      <div className="flex items-center gap-4">
        <Badge variant="success">{onlineCount} Online</Badge>
        <Badge variant="warning">{degradedCount} Degraded</Badge>
        <Badge variant="critical">{offlineCount} Offline</Badge>
      </div>

      {/* Camera Table */}
      <Card padding="none">
        <CardHeader className="px-4 pt-4">
          <CardTitle>Sensor Status ({cameras.length} sensors)</CardTitle>
        </CardHeader>
        <HealthStatusTable cameras={cameras} />
      </Card>

      {/* Self Test */}
      {selfTest && (
        <Card>
          <CardHeader>
            <CardTitle>Nightly Self-Test</CardTitle>
            <Badge variant={selfTest.passed ? 'success' : 'critical'} dot>
              {selfTest.passed ? 'PASS' : 'FAIL'}
            </Badge>
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {selfTest.details.map((d, i) => (
                <div key={i} className="flex items-center gap-2 text-sm">
                  {d.includes('PASS') || d.includes('verified') || d.includes('within') || d.includes('responding') || d.includes('Drift')
                    ? <CheckCircle className="h-4 w-4 text-elder-ok flex-shrink-0" />
                    : <XCircle className="h-4 w-4 text-elder-warning flex-shrink-0" />}
                  <span className="text-elder-text-secondary">{d}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

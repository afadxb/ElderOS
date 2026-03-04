import type { BoardReportData } from '@/types';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { formatResponseTime } from '@/utils/formatters';

interface BoardReportViewProps {
  data: BoardReportData;
}

export function BoardReportView({ data }: BoardReportViewProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6 print:space-y-4">
      <div className="text-center border-b border-elder-border pb-4">
        <h1 className="text-2xl font-bold">ElderOS Vision — Board Report</h1>
        <p className="text-sm text-elder-text-secondary">{data.facilityName} | {data.period}</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Unit Performance Summary</CardTitle></CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Unit</th>
                <th className="text-right py-2">Falls</th>
                <th className="text-right py-2">Avg Response</th>
                <th className="text-right py-2">Unwitnessed Rate</th>
                <th className="text-right py-2">Compliance</th>
              </tr>
            </thead>
            <tbody>
              {data.unitSummaries.map(u => (
                <tr key={u.unit} className="border-b last:border-0">
                  <td className="py-2 font-medium">{u.unit}</td>
                  <td className="text-right py-2">{u.falls}</td>
                  <td className="text-right py-2 font-mono">{formatResponseTime(u.avgResponseTime)}</td>
                  <td className="text-right py-2">{u.unwitnessedRate}%</td>
                  <td className="text-right py-2">{u.complianceScore}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Liability Indicators</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-elder-critical">{data.liabilityIndicators.slowResponses}</p>
              <p className="text-xs text-elder-text-secondary">Slow Responses (&gt;3m)</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-elder-critical">{data.liabilityIndicators.unacknowledgedAlerts}</p>
              <p className="text-xs text-elder-text-secondary">Unacknowledged</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-elder-warning">{data.liabilityIndicators.repeatFalls}</p>
              <p className="text-xs text-elder-text-secondary">Repeat Falls</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

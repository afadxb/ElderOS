import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent, Spinner } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { ShiftSelector } from '@/components/common/ShiftSelector';
import { UnitSelector } from '@/components/common/UnitSelector';
import { PDFExportButton } from '@/components/export/PDFExportButton';
import { formatResponseTime } from '@/utils/formatters';
import * as reportService from '@/services/reportService';
import type { ShiftSummary } from '@/types';
import type { ShiftName } from '@/utils/dateUtils';
import { format } from 'date-fns';

export function ShiftSummaryPage() {
  const [summaries, setSummaries] = useState<ShiftSummary[]>([]);
  const [shift, setShift] = useState<ShiftName | 'all'>('all');
  const [unit, setUnit] = useState('');
  const [loading, setLoading] = useState(true);
  const today = format(new Date(), 'yyyy-MM-dd');

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await reportService.getShiftSummaries(today, unit || undefined);
      setSummaries(data);
      setLoading(false);
    }
    load();
  }, [unit]);

  const filtered = shift === 'all' ? summaries : summaries.filter(s => s.shiftName === shift);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Shift Summary"
        subtitle={`Handoff summary for ${today}`}
        actions={
          <div className="flex items-center gap-2">
            <ShiftSelector value={shift} onChange={setShift} />
            <UnitSelector value={unit} onChange={setUnit} />
            <PDFExportButton type="shift-summary" id={today} label="Export" />
          </div>
        }
      />

      {filtered.length === 0 ? (
        <p className="text-sm text-elder-text-muted text-center py-8">No shift data available for selected filters.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map(s => (
            <Card key={s.shiftId}>
              <CardHeader>
                <CardTitle>{s.shiftName} Shift — {s.unit}</CardTitle>
                <span className="text-xs text-elder-text-muted">{s.startTime}–{s.endTime}</span>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                  <div><span className="text-elder-text-secondary">Total Events</span><p className="font-semibold text-lg">{s.totalEvents}</p></div>
                  <div><span className="text-elder-text-secondary">Falls</span><p className="font-semibold text-lg text-elder-critical">{s.falls}</p></div>
                  <div><span className="text-elder-text-secondary">Avg Ack Time</span><p className="font-mono">{formatResponseTime(s.avgAckTimeSeconds)}</p></div>
                  <div><span className="text-elder-text-secondary">Escalated</span><p className="font-semibold">{s.escalatedCount}</p></div>
                </div>
                {s.notableIncidents.length > 0 && (
                  <div className="border-t border-elder-border pt-2 mt-2">
                    <p className="text-xs font-medium text-elder-text-secondary mb-1">Notable:</p>
                    {s.notableIncidents.map((n, i) => (
                      <p key={i} className="text-xs text-elder-text-primary">{n}</p>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

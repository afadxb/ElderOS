import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Spinner, Button } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { BoardReportView } from '@/components/export/BoardReportView';
import { PDFExportButton } from '@/components/export/PDFExportButton';
import * as reportService from '@/services/reportService';
import type { BoardReportData } from '@/types';
import { ArrowLeft, Printer } from 'lucide-react';

export function BoardReportPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<BoardReportData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const d = await reportService.getBoardReportData();
      setData(d);
      setLoading(false);
    }
    load();
  }, []);

  if (loading || !data) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Board Report"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => window.print()}>
              <Printer className="h-4 w-4 mr-1" /> Print
            </Button>
            <PDFExportButton type="board-report" />
            <Button variant="ghost" size="sm" onClick={() => navigate('/vision/dashboard')}>
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
          </div>
        }
      />
      <BoardReportView data={data} />
    </div>
  );
}

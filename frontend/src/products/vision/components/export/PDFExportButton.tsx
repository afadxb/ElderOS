import { useState } from 'react';
import { Button } from '@/components/ui';
import { Download } from 'lucide-react';
import { generateIncidentPDF, generateBoardReportPDF, generateShiftSummaryPDF } from '@/services/pdfService';
import { downloadBlob } from '@/utils/exportUtils';

interface PDFExportButtonProps {
  type: 'incident' | 'board-report' | 'shift-summary';
  id?: string;
  label?: string;
}

export function PDFExportButton({ type, id, label = 'Download PDF' }: PDFExportButtonProps) {
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    setLoading(true);
    try {
      let blob: Blob;
      let filename: string;
      switch (type) {
        case 'incident':
          blob = await generateIncidentPDF(id || '');
          filename = `incident-${id}.pdf`;
          break;
        case 'board-report':
          blob = await generateBoardReportPDF();
          filename = 'board-report.pdf';
          break;
        case 'shift-summary':
          blob = await generateShiftSummaryPDF(id || '');
          filename = `shift-summary-${id}.pdf`;
          break;
      }
      downloadBlob(blob, filename);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button variant="outline" size="sm" onClick={handleExport} loading={loading}>
      <Download className="h-4 w-4 mr-1.5" />
      {label}
    </Button>
  );
}

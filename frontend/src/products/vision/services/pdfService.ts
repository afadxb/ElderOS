import { simulateLatency } from '@/platform/services/api';

export async function generateIncidentPDF(incidentId: string): Promise<Blob> {
  await simulateLatency();
  const content = `ElderOS Vision - Incident Report\n\nIncident ID: ${incidentId}\nGenerated: ${new Date().toISOString()}\n\n[This is a stub PDF. In production, this would contain the full incident report with timeline, response data, and audit trail.]`;
  return new Blob([content], { type: 'application/pdf' });
}

export async function generateBoardReportPDF(): Promise<Blob> {
  await simulateLatency();
  const content = `ElderOS Vision - Board Report\n\nGenerated: ${new Date().toISOString()}\n\n[This is a stub PDF. In production, this would contain the full board report with trends, KPIs, and liability indicators.]`;
  return new Blob([content], { type: 'application/pdf' });
}

export async function generateShiftSummaryPDF(shiftId: string): Promise<Blob> {
  await simulateLatency();
  const content = `ElderOS Vision - Shift Summary\n\nShift ID: ${shiftId}\nGenerated: ${new Date().toISOString()}\n\n[This is a stub PDF containing shift handoff information.]`;
  return new Blob([content], { type: 'application/pdf' });
}

import type { ShiftSummary } from '@/types';
import { uuid, randomInt, randomPick, randomName } from '../helpers';
import { format, subDays } from 'date-fns';

export function generateShiftSummaries(): ShiftSummary[] {
  const summaries: ShiftSummary[] = [];
  const units = ['Unit A', 'Unit B'];
  const shifts = [
    { name: 'Day', startTime: '07:00', endTime: '15:00' },
    { name: 'Evening', startTime: '15:00', endTime: '23:00' },
    { name: 'Night', startTime: '23:00', endTime: '07:00' },
  ];

  for (let day = 0; day < 7; day++) {
    const date = subDays(new Date(), day);
    const dateStr = format(date, 'yyyy-MM-dd');

    for (const unit of units) {
      for (const shift of shifts) {
        const falls = randomInt(0, 4);
        const bedExits = randomInt(1, 8);
        const inactivity = randomInt(0, 5);
        const unsafeTransfers = randomInt(0, 2);
        const totalEvents = falls + bedExits + inactivity + unsafeTransfers;

        summaries.push({
          shiftId: uuid(),
          shiftName: shift.name,
          date: dateStr,
          startTime: shift.startTime,
          endTime: shift.endTime,
          unit,
          totalEvents,
          falls,
          bedExits,
          inactivityAlerts: inactivity,
          unsafeTransfers,
          avgAckTimeSeconds: randomInt(30, 180),
          avgResolveTimeSeconds: randomInt(90, 420),
          unacknowledgedCount: randomInt(0, 2),
          escalatedCount: randomInt(0, 1),
          highRiskResidents: Array.from({ length: randomInt(1, 4) }, () => randomName().full),
          notableIncidents: falls > 0
            ? [`Fall in Room ${randomInt(101, 225)} — ${randomPick(['resolved quickly', 'required escalation', 'repeat fall'])}`]
            : [],
        });
      }
    }
  }

  return summaries;
}

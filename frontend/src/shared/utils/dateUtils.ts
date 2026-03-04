import { startOfDay, addHours } from 'date-fns';

export type ShiftName = 'Day' | 'Evening' | 'Night';

export interface ShiftBoundary {
  name: ShiftName;
  startHour: number;
  endHour: number;
}

export const SHIFTS: ShiftBoundary[] = [
  { name: 'Day', startHour: 7, endHour: 15 },
  { name: 'Evening', startHour: 15, endHour: 23 },
  { name: 'Night', startHour: 23, endHour: 7 },
];

export function getCurrentShift(): ShiftName {
  const hour = new Date().getHours();
  if (hour >= 7 && hour < 15) return 'Day';
  if (hour >= 15 && hour < 23) return 'Evening';
  return 'Night';
}

export function getShiftBounds(date: Date, shift: ShiftName): { start: Date; end: Date } {
  const s = SHIFTS.find(s => s.name === shift)!;
  const dayStart = startOfDay(date);
  if (shift === 'Night') {
    return {
      start: addHours(dayStart, 23),
      end: addHours(dayStart, 31),
    };
  }
  return {
    start: addHours(dayStart, s.startHour),
    end: addHours(dayStart, s.endHour),
  };
}

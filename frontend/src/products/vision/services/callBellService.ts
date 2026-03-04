import type {
  CallBellEvent,
  CallBellStaffMetrics,
  CallBellFloorMetrics,
  CallBellShiftMetrics,
  CallBellDailySummary,
  PaginatedResponse,
} from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

interface CallBellFilters {
  unit?: string;
  floor?: number;
  shift?: string;
  priority?: string;
  status?: string;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  pageSize?: number;
}

export async function getCallBellEvents(
  filters: CallBellFilters = {}
): Promise<PaginatedResponse<CallBellEvent>> {
  await simulateLatency();
  let events = [...mockStore.callBellEvents];

  if (filters.unit) events = events.filter(e => e.unit === filters.unit);
  if (filters.floor !== undefined) events = events.filter(e => e.floor === filters.floor);
  if (filters.shift) events = events.filter(e => e.shift === filters.shift);
  if (filters.priority) events = events.filter(e => e.priority === filters.priority);
  if (filters.status) events = events.filter(e => e.status === filters.status);
  if (filters.dateFrom) {
    const from = new Date(filters.dateFrom).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() >= from);
  }
  if (filters.dateTo) {
    const to = new Date(filters.dateTo).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() <= to);
  }

  const page = filters.page || 1;
  const pageSize = filters.pageSize || 20;
  const total = events.length;
  const totalPages = Math.ceil(total / pageSize);
  const start = (page - 1) * pageSize;
  const data = events.slice(start, start + pageSize);

  return { data, total, page, pageSize, totalPages };
}

export async function getActiveCallBells(): Promise<CallBellEvent[]> {
  await simulateLatency();
  return mockStore.getActiveCallBells();
}

export async function respondToCallBell(
  eventId: string,
  userId: string,
  userName: string
): Promise<CallBellEvent | undefined> {
  await simulateLatency();
  return mockStore.respondToCallBell(eventId, userId, userName);
}

export async function closeCallBell(eventId: string): Promise<CallBellEvent | undefined> {
  await simulateLatency();
  return mockStore.closeCallBell(eventId);
}

export async function getStaffMetrics(
  filters: { unit?: string; dateFrom?: string; dateTo?: string } = {}
): Promise<CallBellStaffMetrics[]> {
  await simulateLatency();
  let events = mockStore.callBellEvents.filter(
    e => e.status === 'responded' || e.status === 'closed'
  );

  if (filters.unit) events = events.filter(e => e.unit === filters.unit);
  if (filters.dateFrom) {
    const from = new Date(filters.dateFrom).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() >= from);
  }
  if (filters.dateTo) {
    const to = new Date(filters.dateTo).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() <= to);
  }

  const staffMap = new Map<string, CallBellEvent[]>();
  for (const e of events) {
    if (!e.respondedBy) continue;
    const existing = staffMap.get(e.respondedBy) || [];
    existing.push(e);
    staffMap.set(e.respondedBy, existing);
  }

  const metrics: CallBellStaffMetrics[] = [];
  for (const [staffId, staffEvents] of staffMap) {
    const times = staffEvents
      .map(e => e.responseTimeSeconds)
      .filter((t): t is number => t !== null)
      .sort((a, b) => a - b);

    if (times.length === 0) continue;

    const avg = Math.round(times.reduce((s, t) => s + t, 0) / times.length);
    const median = times[Math.floor(times.length / 2)];

    metrics.push({
      staffId,
      staffName: staffEvents[0].respondedByName || staffId,
      role: staffId.startsWith('nurse') ? 'Nurse' : 'PSW',
      totalCalls: staffEvents.length,
      avgResponseSeconds: avg,
      medianResponseSeconds: median,
      minResponseSeconds: times[0],
      maxResponseSeconds: times[times.length - 1],
      callsUnder60s: times.filter(t => t <= 60).length,
      callsUnder120s: times.filter(t => t <= 120).length,
      callsOver180s: times.filter(t => t > 180).length,
    });
  }

  metrics.sort((a, b) => a.avgResponseSeconds - b.avgResponseSeconds);
  return metrics;
}

export async function getFloorMetrics(
  filters: { dateFrom?: string; dateTo?: string } = {}
): Promise<CallBellFloorMetrics[]> {
  await simulateLatency();
  let events = mockStore.callBellEvents.filter(e => e.responseTimeSeconds !== null);

  if (filters.dateFrom) {
    const from = new Date(filters.dateFrom).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() >= from);
  }
  if (filters.dateTo) {
    const to = new Date(filters.dateTo).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() <= to);
  }

  const floorMap = new Map<string, CallBellEvent[]>();
  for (const e of events) {
    const key = `${e.floor}-${e.unit}`;
    const existing = floorMap.get(key) || [];
    existing.push(e);
    floorMap.set(key, existing);
  }

  const metrics: CallBellFloorMetrics[] = [];
  for (const [, floorEvents] of floorMap) {
    const times = floorEvents
      .map(e => e.responseTimeSeconds)
      .filter((t): t is number => t !== null)
      .sort((a, b) => a - b);

    const avg = times.length > 0
      ? Math.round(times.reduce((s, t) => s + t, 0) / times.length)
      : 0;

    const callsByPriority = { emergency: 0, urgent: 0, normal: 0 } as Record<string, number>;
    for (const e of floorEvents) callsByPriority[e.priority]++;

    const callsByOrigin = { bedside: 0, bathroom: 0, hallway: 0, pendant: 0 } as Record<string, number>;
    for (const e of floorEvents) callsByOrigin[e.origin]++;

    const hourCounts = new Array(24).fill(0);
    for (const e of floorEvents) {
      hourCounts[new Date(e.pressedAt).getHours()]++;
    }
    const peakHour = hourCounts.indexOf(Math.max(...hourCounts));

    metrics.push({
      floor: floorEvents[0].floor,
      unit: floorEvents[0].unit,
      totalCalls: floorEvents.length,
      avgResponseSeconds: avg,
      callsByPriority: callsByPriority as CallBellFloorMetrics['callsByPriority'],
      callsByOrigin: callsByOrigin as CallBellFloorMetrics['callsByOrigin'],
      peakHour,
    });
  }

  return metrics;
}

export async function getShiftMetrics(
  filters: { unit?: string; dateFrom?: string; dateTo?: string } = {}
): Promise<CallBellShiftMetrics[]> {
  await simulateLatency();
  let events = [...mockStore.callBellEvents];

  if (filters.unit) events = events.filter(e => e.unit === filters.unit);
  if (filters.dateFrom) {
    const from = new Date(filters.dateFrom).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() >= from);
  }
  if (filters.dateTo) {
    const to = new Date(filters.dateTo).getTime();
    events = events.filter(e => new Date(e.pressedAt).getTime() <= to);
  }

  // Group by shift name (aggregate across all dates/units)
  const shiftMap = new Map<string, CallBellEvent[]>();
  for (const e of events) {
    const existing = shiftMap.get(e.shift) || [];
    existing.push(e);
    shiftMap.set(e.shift, existing);
  }

  const metrics: CallBellShiftMetrics[] = [];
  for (const [shift, shiftEvents] of shiftMap) {
    const times = shiftEvents
      .map(e => e.responseTimeSeconds)
      .filter((t): t is number => t !== null)
      .sort((a, b) => a - b);

    const avg = times.length > 0
      ? Math.round(times.reduce((s, t) => s + t, 0) / times.length)
      : 0;

    metrics.push({
      shift: shift as 'Day' | 'Evening' | 'Night',
      date: '',
      unit: filters.unit || 'All',
      totalCalls: shiftEvents.length,
      avgResponseSeconds: avg,
      respondedWithin60s: times.filter(t => t <= 60).length,
      respondedWithin120s: times.filter(t => t <= 120).length,
      slowResponses: times.filter(t => t > 180).length,
    });
  }

  // Sort Day, Evening, Night
  const order = { Day: 0, Evening: 1, Night: 2 };
  metrics.sort((a, b) => order[a.shift] - order[b.shift]);
  return metrics;
}

export async function getDailySummaries(
  filters: { unit?: string } = {}
): Promise<CallBellDailySummary[]> {
  await simulateLatency();
  let events = [...mockStore.callBellEvents];
  if (filters.unit) events = events.filter(e => e.unit === filters.unit);

  const dayMap = new Map<string, CallBellEvent[]>();
  for (const e of events) {
    const date = e.pressedAt.slice(0, 10);
    const existing = dayMap.get(date) || [];
    existing.push(e);
    dayMap.set(date, existing);
  }

  const summaries: CallBellDailySummary[] = [];
  for (const [date, dayEvents] of dayMap) {
    const responded = dayEvents.filter(e => e.responseTimeSeconds !== null);
    const avg = responded.length > 0
      ? Math.round(responded.reduce((s, e) => s + e.responseTimeSeconds!, 0) / responded.length)
      : 0;

    summaries.push({ date, totalCalls: dayEvents.length, avgResponseSeconds: avg });
  }

  summaries.sort((a, b) => a.date.localeCompare(b.date));
  return summaries;
}

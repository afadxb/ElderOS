// Seeded random for deterministic mock data
let seed = 42;
export function seededRandom(): number {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
}

export function resetSeed(s: number = 42): void {
  seed = s;
}

export function randomInt(min: number, max: number): number {
  return Math.floor(seededRandom() * (max - min + 1)) + min;
}

export function randomFloat(min: number, max: number): number {
  return seededRandom() * (max - min) + min;
}

export function randomPick<T>(arr: T[]): T {
  return arr[randomInt(0, arr.length - 1)];
}

export function randomPicks<T>(arr: T[], count: number): T[] {
  const shuffled = [...arr].sort(() => seededRandom() - 0.5);
  return shuffled.slice(0, count);
}

export function uuid(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (seededRandom() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function randomDate(start: Date, end: Date): Date {
  const startTime = start.getTime();
  const endTime = end.getTime();
  return new Date(startTime + seededRandom() * (endTime - startTime));
}

export const FIRST_NAMES = [
  'Margaret', 'Dorothy', 'Helen', 'Betty', 'Ruth', 'Shirley', 'Virginia', 'Barbara',
  'Jean', 'Frances', 'Robert', 'James', 'John', 'William', 'Richard', 'Charles',
  'Donald', 'George', 'Thomas', 'Edward', 'Mary', 'Patricia', 'Elizabeth', 'Joan',
  'Alice', 'Harold', 'Frank', 'Arthur', 'Henry', 'Walter', 'Rose', 'Evelyn',
  'Florence', 'Mildred', 'Gladys', 'Lillian', 'Catherine', 'Irene', 'Marie', 'Ann',
];

export const LAST_NAMES = [
  'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
  'Rodriguez', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Jackson', 'White',
  'Harris', 'Clark', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
  'Wright', 'Scott', 'Green', 'Baker', 'Adams', 'Nelson', 'Campbell',
];

export function randomName(): { first: string; last: string; full: string } {
  const first = randomPick(FIRST_NAMES);
  const last = randomPick(LAST_NAMES);
  return { first, last, full: `${first} ${last}` };
}

export function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

export const PRE_EVENT_SUMMARIES = [
  'Resident was ambulatory in room, moving between bed and bathroom area.',
  'Resident was seated on bed edge, appeared to be preparing to stand.',
  'Resident was lying in bed with periodic movement detected.',
  'Resident was standing near bedside, holding onto bed rail.',
  'Resident was walking slowly across room toward doorway.',
  'Resident was attempting to transfer from wheelchair to bed independently.',
  'Resident was sitting in wheelchair near window, minimal movement.',
  'Resident appeared restless, multiple position changes detected in last 10 minutes.',
];

export const POST_EVENT_STATES = [
  'Resident found on floor beside bed. Alert and responsive.',
  'Resident on floor near bathroom doorway. No visible distress.',
  'Resident lying on floor at foot of bed. Conscious but disoriented.',
  'Resident seated on floor next to wheelchair. Appears stable.',
  'Resident standing with support of bed rail after near-fall event.',
  'Resident returned to bed after bed exit alert. No injury observed.',
  'Resident found seated on floor. Staff attended within alert window.',
  'Resident stable in bed after prolonged inactivity alert triggered.',
];

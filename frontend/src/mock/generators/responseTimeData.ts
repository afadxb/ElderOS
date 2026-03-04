import { randomInt } from '../helpers';

export interface ResponseTimeBucket {
  range: string;
  count: number;
  minSeconds: number;
  maxSeconds: number;
}

export function generateResponseTimeDistribution(): ResponseTimeBucket[] {
  return [
    { range: '0-30s', count: randomInt(15, 35), minSeconds: 0, maxSeconds: 30 },
    { range: '30-60s', count: randomInt(40, 80), minSeconds: 30, maxSeconds: 60 },
    { range: '1-2m', count: randomInt(60, 120), minSeconds: 60, maxSeconds: 120 },
    { range: '2-3m', count: randomInt(30, 60), minSeconds: 120, maxSeconds: 180 },
    { range: '3-5m', count: randomInt(10, 25), minSeconds: 180, maxSeconds: 300 },
    { range: '5m+', count: randomInt(2, 10), minSeconds: 300, maxSeconds: 600 },
  ];
}

export interface MonthlyTrend {
  month: string;
  falls: number;
  avgResponseTime: number;
  unwitnessedRate: number;
}

export function generateMonthlyTrends(): MonthlyTrend[] {
  const months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'];
  return months.map((month, i) => ({
    month,
    falls: Math.max(5, 30 - i * 2 + randomInt(-3, 3)), // declining trend
    avgResponseTime: Math.max(45, 120 - i * 5 + randomInt(-10, 10)), // improving
    unwitnessedRate: Math.max(5, 40 - i * 3 + randomInt(-2, 2)), // improving
  }));
}

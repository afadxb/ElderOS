import { useState, useCallback } from 'react';
import { useInterval } from './useInterval';
import { differenceInSeconds } from 'date-fns';

interface CountdownResult {
  elapsed: number;
  remaining: number;
  isExpired: boolean;
  formatted: string;
}

export function useCountdown(escalationThresholdSeconds: number, startedAt: string | null): CountdownResult {
  const [now, setNow] = useState(Date.now());

  useInterval(() => setNow(Date.now()), 1000);

  if (!startedAt) {
    return { elapsed: 0, remaining: escalationThresholdSeconds, isExpired: false, formatted: '--:--' };
  }

  const elapsed = differenceInSeconds(new Date(now), new Date(startedAt));
  const remaining = Math.max(0, escalationThresholdSeconds - elapsed);
  const isExpired = remaining <= 0;

  const displaySeconds = isExpired ? elapsed : remaining;
  const min = Math.floor(displaySeconds / 60);
  const sec = displaySeconds % 60;
  const formatted = `${min}:${sec.toString().padStart(2, '0')}`;

  return { elapsed, remaining, isExpired, formatted };
}

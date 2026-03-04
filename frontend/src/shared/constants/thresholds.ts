export const DEFAULT_CONFIDENCE_THRESHOLDS = {
  highMin: 85,
  mediumMin: 60,
  lowMin: 30,
} as const;

export const DEFAULT_ESCALATION_INTERVALS = {
  level1Seconds: 120,
  level2Seconds: 300,
  level3Seconds: 600,
} as const;

export const RESPONSE_TIME_THRESHOLDS = {
  ackGoodSeconds: 60,
  ackWarningSeconds: 120,
  ackCriticalSeconds: 180,
  resolveGoodSeconds: 180,
  resolveWarningSeconds: 300,
  resolveCriticalSeconds: 600,
} as const;

export const RISK_SCORE_THRESHOLDS = {
  low: 40,
  medium: 70,
  high: 100,
} as const;

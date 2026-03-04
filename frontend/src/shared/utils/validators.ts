export function isValidRetentionDays(days: number): boolean {
  return days >= 3 && days <= 14;
}

export function isValidConfidenceThreshold(value: number): boolean {
  return value >= 0 && value <= 100;
}

export function isValidEscalationDelay(minutes: number): boolean {
  return minutes >= 1 && minutes <= 60;
}

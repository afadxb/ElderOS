import type { RiskTrend } from '@/types';

export function getRiskLevel(score: number): 'low' | 'medium' | 'high' {
  if (score >= 71) return 'high';
  if (score >= 41) return 'medium';
  return 'low';
}

export function getRiskLabel(score: number): string {
  const level = getRiskLevel(score);
  return { low: 'Low Risk', medium: 'Medium Risk', high: 'High Risk' }[level];
}

export function getTrendIcon(trend: RiskTrend): string {
  return { rising: 'TrendingUp', stable: 'Minus', declining: 'TrendingDown' }[trend];
}

export function getTrendColor(trend: RiskTrend): string {
  return { rising: 'text-elder-critical', stable: 'text-elder-text-secondary', declining: 'text-elder-ok' }[trend];
}

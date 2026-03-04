import type { EscalationRule, ConfidenceThresholds, RetentionPolicy, ExclusionZone } from '@/types';
import { mockStore } from '@/mock';
import { simulateLatency } from '@/platform/services/api';

export async function getEscalationRules(): Promise<EscalationRule[]> {
  await simulateLatency();
  return mockStore.settings.escalationRules;
}

export async function updateEscalationRule(rule: EscalationRule): Promise<void> {
  await simulateLatency();
  const idx = mockStore.settings.escalationRules.findIndex(r => r.id === rule.id);
  if (idx >= 0) mockStore.settings.escalationRules[idx] = rule;
}

export async function getConfidenceThresholds(): Promise<ConfidenceThresholds> {
  await simulateLatency();
  return mockStore.settings.confidenceThresholds;
}

export async function updateConfidenceThresholds(t: ConfidenceThresholds): Promise<void> {
  await simulateLatency();
  mockStore.settings.confidenceThresholds = t;
}

export async function getRetentionPolicy(): Promise<RetentionPolicy> {
  await simulateLatency();
  return mockStore.settings.retention;
}

export async function updateRetentionPolicy(p: RetentionPolicy): Promise<void> {
  await simulateLatency();
  mockStore.settings.retention = p;
}

export async function getExclusionZones(): Promise<ExclusionZone[]> {
  await simulateLatency();
  return mockStore.settings.exclusionZones;
}

export async function updateExclusionZone(zone: ExclusionZone): Promise<void> {
  await simulateLatency();
  const idx = mockStore.settings.exclusionZones.findIndex(z => z.id === zone.id);
  if (idx >= 0) mockStore.settings.exclusionZones[idx] = zone;
}

export interface EscalationRule {
  id: string;
  delayMinutes: number;
  action: 'sms' | 'page' | 'call' | 'email';
  target: string;
  enabled: boolean;
}

export interface ConfidenceThresholds {
  highMin: number;
  mediumMin: number;
  lowMin: number;
}

export interface RetentionPolicy {
  clipRetentionDays: number;
  metadataRetentionDays: number;
  autoPurgeEnabled: boolean;
  purgeThresholdPercent: number;
}

export interface ExclusionZone {
  id: string;
  roomId: string;
  roomNumber: string;
  zoneName: string;
  enabled: boolean;
}

export interface RolePermissionSet {
  role: string;
  permissions: string[];
}

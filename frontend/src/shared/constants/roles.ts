import type { UserRole, Permission } from '@/types/auth';

export const ROLE_LABELS: Record<UserRole, string> = {
  psw: 'PSW',
  nurse: 'Nurse',
  supervisor: 'Supervisor',
  executive: 'Executive',
  admin: 'IT Admin',
};

export const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  psw: [
    'vision:alerts:view', 'vision:alerts:acknowledge', 'vision:alerts:resolve',
    'vision:rooms:view', 'vision:incidents:view', 'vision:residents:view',
    'vision:callbell:view', 'vision:callbell:respond',
  ],
  nurse: [
    'vision:alerts:view', 'vision:alerts:acknowledge', 'vision:alerts:resolve',
    'vision:rooms:view', 'vision:incidents:view', 'vision:incidents:export',
    'vision:residents:view', 'vision:reports:view',
    'vision:callbell:view', 'vision:callbell:respond',
  ],
  supervisor: [
    'vision:alerts:view', 'vision:alerts:acknowledge', 'vision:alerts:resolve',
    'vision:rooms:view', 'vision:incidents:view', 'vision:incidents:export',
    'vision:review:view', 'vision:review:triage',
    'vision:residents:view', 'vision:clips:request', 'vision:clips:view',
    'vision:reports:view',
    'vision:callbell:view', 'vision:callbell:respond', 'vision:callbell:analytics',
  ],
  executive: [
    'vision:rooms:view', 'vision:incidents:view', 'vision:incidents:export',
    'vision:residents:view', 'vision:reports:view', 'vision:reports:board',
    'vision:callbell:view', 'vision:callbell:analytics',
  ],
  admin: [
    'vision:alerts:view', 'vision:rooms:view', 'vision:incidents:view',
    'platform:system:view', 'platform:system:manage',
    'platform:settings:view', 'platform:settings:manage',
  ],
};

export const ROLE_HOME_ROUTES: Record<UserRole, string> = {
  psw: '/vision/alerts',
  nurse: '/vision/alerts',
  supervisor: '/vision/alerts',
  executive: '/vision/dashboard',
  admin: '/system',
};

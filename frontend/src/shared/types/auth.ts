export type UserRole = 'psw' | 'nurse' | 'supervisor' | 'executive' | 'admin';

export interface User {
  id: string;
  name: string;
  role: UserRole;
  unit: string;
  email: string;
  avatarInitials: string;
}

export interface Session {
  user: User;
  loginAt: string;
  expiresAt: string;
}

export type Permission =
  // Vision product permissions
  | 'vision:alerts:view'
  | 'vision:alerts:acknowledge'
  | 'vision:alerts:resolve'
  | 'vision:rooms:view'
  | 'vision:incidents:view'
  | 'vision:incidents:export'
  | 'vision:review:view'
  | 'vision:review:triage'
  | 'vision:residents:view'
  | 'vision:clips:request'
  | 'vision:clips:view'
  | 'vision:reports:view'
  | 'vision:reports:board'
  // Call Bell permissions
  | 'vision:callbell:view'
  | 'vision:callbell:respond'
  | 'vision:callbell:analytics'
  // Platform permissions
  | 'platform:system:view'
  | 'platform:system:manage'
  | 'platform:settings:view'
  | 'platform:settings:manage';

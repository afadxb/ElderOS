import type { User, UserRole } from '@/types';
import { simulateLatency } from './api';

const MOCK_USERS: Record<UserRole, User> = {
  psw: {
    id: 'psw-1',
    name: 'Sarah Chen',
    role: 'psw',
    unit: 'Unit A',
    email: 'sarah.chen@facility.local',
    avatarInitials: 'SC',
  },
  nurse: {
    id: 'nurse-1',
    name: 'Amanda Liu',
    role: 'nurse',
    unit: 'Unit A',
    email: 'amanda.liu@facility.local',
    avatarInitials: 'AL',
  },
  supervisor: {
    id: 'supervisor-1',
    name: 'Michael Torres',
    role: 'supervisor',
    unit: 'Unit A',
    email: 'michael.torres@facility.local',
    avatarInitials: 'MT',
  },
  executive: {
    id: 'executive-1',
    name: 'Jennifer Walsh',
    role: 'executive',
    unit: 'All Units',
    email: 'jennifer.walsh@facility.local',
    avatarInitials: 'JW',
  },
  admin: {
    id: 'admin-1',
    name: 'David Kim',
    role: 'admin',
    unit: 'All Units',
    email: 'david.kim@facility.local',
    avatarInitials: 'DK',
  },
};

export async function loginByRole(role: UserRole): Promise<User> {
  await simulateLatency();
  return MOCK_USERS[role];
}

export async function getCurrentUser(role: UserRole): Promise<User> {
  return MOCK_USERS[role];
}

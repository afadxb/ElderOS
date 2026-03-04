import type { UserRole } from '@/types';

export const ROLE_NAV_ITEMS: Record<UserRole, string[]> = {
  psw: ['/vision/alerts', '/vision/rooms', '/vision/residents', '/vision/incidents'],
  nurse: ['/vision/alerts', '/vision/rooms', '/vision/incidents', '/vision/residents', '/vision/shifts', '/vision/reports'],
  supervisor: ['/vision/alerts', '/vision/review', '/vision/rooms', '/vision/incidents', '/vision/residents', '/vision/shifts', '/vision/reports'],
  executive: ['/vision/dashboard', '/vision/rooms', '/vision/incidents', '/vision/residents', '/vision/reports', '/vision/board-report'],
  admin: ['/system', '/facility', '/settings', '/vision/rooms', '/vision/incidents'],
};

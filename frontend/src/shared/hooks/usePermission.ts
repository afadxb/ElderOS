import type { Permission } from '@/types';
import { useAuth } from './useAuth';

export function usePermission(permission: Permission): boolean {
  const { hasPermission } = useAuth();
  return hasPermission(permission);
}

export function useRequirePermission(permission: Permission): void {
  const allowed = usePermission(permission);
  if (!allowed) {
    throw new Error(`Permission denied: ${permission}`);
  }
}

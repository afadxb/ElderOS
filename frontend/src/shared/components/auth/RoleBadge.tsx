import { Badge } from '@/components/ui';
import type { UserRole } from '@/types';
import { ROLE_LABELS } from '@/constants';

interface RoleBadgeProps {
  role: UserRole;
}

export function RoleBadge({ role }: RoleBadgeProps) {
  return <Badge variant="info">{ROLE_LABELS[role]}</Badge>;
}

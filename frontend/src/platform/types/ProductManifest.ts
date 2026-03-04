import type { FC, LazyExoticComponent } from 'react';
import type { LucideIcon } from 'lucide-react';
import type { UserRole } from '@/types';

export interface ProductManifest {
  id: string;
  name: string;
  icon: LucideIcon;
  routes: () => Promise<{ default: FC }>;
  navItems: ProductNavItem[];
  widgets?: DashboardWidget[];
}

export interface ProductNavItem {
  label: string;
  path: string;
  icon: LucideIcon;
  roles: UserRole[];
  badgeCount?: () => number;
}

export interface DashboardWidget {
  id: string;
  component: LazyExoticComponent<FC>;
  roles: UserRole[];
  size: 'sm' | 'md' | 'lg' | 'full';
  priority: number;
  section: 'alerts' | 'status' | 'metrics';
}

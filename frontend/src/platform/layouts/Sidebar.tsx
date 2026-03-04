import { NavLink } from 'react-router-dom';
import { Activity, Building2, Cpu, Settings, ChevronLeft, ChevronRight, Shield } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useAlertStore } from '@/platform/stores/alertStore';
import { registeredProducts } from '@/platform/registry';
import { cn } from '@/utils/cn';
import type { UserRole } from '@/types';
import type { ProductNavItem } from '@/platform/types/ProductManifest';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

// Platform-level nav items (always at bottom, independent of product)
const platformNavItems: { label: string; path: string; icon: typeof Activity; roles: UserRole[] }[] = [
  { label: 'Facility', path: '/facility', icon: Building2, roles: ['admin'] },
  { label: 'Devices', path: '/devices', icon: Cpu, roles: ['admin'] },
  { label: 'System Health', path: '/system', icon: Activity, roles: ['admin'] },
  { label: 'Settings', path: '/settings', icon: Settings, roles: ['admin'] },
];

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { user } = useAuth();
  const unacknowledgedCount = useAlertStore((s) => s.unacknowledgedCount);

  if (!user) return null;

  // Collect nav items from all registered products, filtered by role
  const productNavItems: (ProductNavItem & { badge?: number })[] = registeredProducts
    .flatMap((product) => product.navItems)
    .filter((item) => item.roles.includes(user.role))
    .map((item) => ({
      ...item,
      badge: item.label === 'Alerts' ? unacknowledgedCount : undefined,
    }));

  const filteredPlatformItems = platformNavItems.filter((item) => item.roles.includes(user.role));
  const showProductRail = registeredProducts.length > 1;

  return (
    <aside
      className={cn(
        'hidden lg:flex bg-elder-surface border-r border-elder-border h-screen sticky top-0 transition-all duration-200 z-20',
        collapsed ? 'w-sidebar-collapsed' : 'w-sidebar-w'
      )}
    >
      {/* Product rail — only shown when multiple products registered */}
      {showProductRail && (
        <div className="w-12 flex flex-col items-center py-3 gap-2 border-r border-elder-border bg-elder-surface-alt">
          {registeredProducts.map((product) => (
            <NavLink
              key={product.id}
              to={`/${product.id}`}
              className={({ isActive }) =>
                cn(
                  'flex items-center justify-center h-10 w-10 rounded-lg transition-colors',
                  isActive
                    ? 'bg-elder-action-bg text-elder-action'
                    : 'text-elder-text-muted hover:bg-elder-surface hover:text-elder-text-primary'
                )
              }
              title={product.name}
            >
              <product.icon className="h-5 w-5" />
            </NavLink>
          ))}
        </div>
      )}

      {/* Main navigation panel */}
      <div className="flex flex-col flex-1 min-w-0">
        <div className={cn('flex items-center h-topbar-h px-4 border-b border-elder-border', collapsed ? 'justify-center' : 'gap-2')}>
          <Shield className="h-6 w-6 text-elder-action flex-shrink-0" />
          {!collapsed && <span className="font-bold text-sm text-elder-text-primary">ElderOS</span>}
        </div>

        <nav className="flex-1 py-2 overflow-y-auto scrollbar-thin">
          {/* Product nav items */}
          {productNavItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-colors mx-2 rounded-md',
                  isActive
                    ? 'bg-elder-action-bg text-elder-action'
                    : 'text-elder-text-secondary hover:bg-elder-surface-alt hover:text-elder-text-primary',
                  collapsed && 'justify-center px-2'
                )
              }
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && (
                <>
                  <span className="flex-1">{item.label}</span>
                  {item.badge !== undefined && item.badge > 0 && (
                    <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-elder-critical text-[10px] font-bold text-white px-1.5">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          ))}

          {/* Divider before platform items */}
          {filteredPlatformItems.length > 0 && productNavItems.length > 0 && (
            <div className="mx-4 my-2 border-t border-elder-border" />
          )}

          {/* Platform nav items */}
          {filteredPlatformItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-4 py-2.5 text-sm font-medium transition-colors mx-2 rounded-md',
                  isActive
                    ? 'bg-elder-action-bg text-elder-action'
                    : 'text-elder-text-secondary hover:bg-elder-surface-alt hover:text-elder-text-primary',
                  collapsed && 'justify-center px-2'
                )
              }
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span className="flex-1">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        <button
          onClick={onToggle}
          className="flex items-center justify-center h-10 border-t border-elder-border text-elder-text-muted hover:text-elder-text-primary"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  );
}

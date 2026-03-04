import { NavLink } from 'react-router-dom';
import { Bell, LayoutGrid, Users, MoreHorizontal } from 'lucide-react';
import { useAlertStore } from '@/platform/stores/alertStore';
import { cn } from '@/utils/cn';

export function MobileBottomNav() {
  const unacknowledgedCount = useAlertStore((s) => s.unacknowledgedCount);

  const items = [
    { label: 'Alerts', path: '/vision/alerts', icon: Bell, badge: unacknowledgedCount },
    { label: 'Rooms', path: '/vision/rooms', icon: LayoutGrid },
    { label: 'Residents', path: '/vision/residents', icon: Users },
    { label: 'More', path: '/vision/incidents', icon: MoreHorizontal },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 h-bottom-nav bg-elder-surface border-t border-elder-border flex items-center justify-around z-30 lg:hidden">
      {items.map(item => (
        <NavLink
          key={item.path}
          to={item.path}
          className={({ isActive }) =>
            cn(
              'flex flex-col items-center justify-center gap-0.5 flex-1 h-full text-[10px] font-medium transition-colors',
              isActive ? 'text-elder-action' : 'text-elder-text-muted'
            )
          }
        >
          <div className="relative">
            <item.icon className="h-5 w-5" />
            {item.badge !== undefined && item.badge > 0 && (
              <span className="absolute -top-1 -right-1.5 flex h-3.5 min-w-[0.875rem] items-center justify-center rounded-full bg-elder-critical text-[8px] font-bold text-white px-1">
                {item.badge}
              </span>
            )}
          </div>
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

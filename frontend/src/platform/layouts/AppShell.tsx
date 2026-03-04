import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { MobileBottomNav } from './MobileBottomNav';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/utils/cn';

export function AppShell() {
  const { user } = useAuth();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const isPsw = user?.role === 'psw';

  return (
    <div className="flex h-screen overflow-hidden">
      {!isPsw && (
        <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} />
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <Topbar onMenuToggle={() => setSidebarCollapsed(!sidebarCollapsed)} showMenu={!isPsw} />

        <main
          className={cn(
            'flex-1 overflow-y-auto p-4 lg:p-6',
            isPsw && 'pb-20 lg:pb-6'
          )}
        >
          <Outlet />
        </main>

        {isPsw && <MobileBottomNav />}
      </div>
    </div>
  );
}

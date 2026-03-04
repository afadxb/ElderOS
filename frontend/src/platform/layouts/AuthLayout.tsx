import { Outlet } from 'react-router-dom';

export function AuthLayout() {
  return (
    <div className="min-h-screen bg-elder-surface-alt flex items-center justify-center p-4">
      <Outlet />
    </div>
  );
}

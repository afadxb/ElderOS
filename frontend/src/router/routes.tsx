import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { ROLE_HOME_ROUTES } from '@/constants';
import { AuthLayout } from '@/layouts/AuthLayout';
import { AppShell } from '@/layouts/AppShell';
import { ProtectedRoute } from './ProtectedRoute';
import { LoginPage } from '@/pages/LoginPage';
import { NotFoundPage } from '@/pages/NotFoundPage';
import { SystemHealthPage } from '@/pages/admin/SystemHealthPage';
import { SettingsPage } from '@/pages/admin/SettingsPage';
import { FacilityManagementPage } from '@/pages/admin/FacilityManagementPage';
import { DeviceManagementPage } from '@/pages/admin/DeviceManagementPage';

const VisionRoutes = lazy(() => import('@/products/vision/routes'));

export function AppRoutes() {
  const { isAuthenticated, user } = useAuth();

  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to={ROLE_HOME_ROUTES[user!.role]} replace /> : <LoginPage />}
        />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          {/* Vision product — lazy loaded */}
          <Route path="/vision/*" element={
            <Suspense fallback={<div className="flex items-center justify-center h-64 text-elder-text-secondary">Loading...</div>}>
              <VisionRoutes />
            </Suspense>
          } />

          {/* Platform: Admin */}
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/facility" element={<FacilityManagementPage />} />
            <Route path="/devices" element={<DeviceManagementPage />} />
            <Route path="/system" element={<SystemHealthPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          {/* Root redirect */}
          <Route path="/" element={
            isAuthenticated && user
              ? <Navigate to={ROLE_HOME_ROUTES[user.role]} replace />
              : <Navigate to="/login" replace />
          } />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

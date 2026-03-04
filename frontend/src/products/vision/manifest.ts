import { Eye, Bell, BellRing, LayoutGrid, ClipboardCheck, FileText, Users, Clock, BarChart3 } from 'lucide-react';
import type { ProductManifest } from '@/platform/types/ProductManifest';

export const visionManifest: ProductManifest = {
  id: 'vision',
  name: 'ElderOS Vision',
  icon: Eye,
  routes: () => import('./routes'),
  navItems: [
    { label: 'Alerts', path: '/vision/alerts', icon: Bell, roles: ['psw', 'nurse', 'supervisor'] },
    { label: 'Room Grid', path: '/vision/rooms', icon: LayoutGrid, roles: ['psw', 'nurse', 'supervisor', 'executive', 'admin'] },
    { label: 'Review Queue', path: '/vision/review', icon: ClipboardCheck, roles: ['supervisor'] },
    { label: 'Incidents', path: '/vision/incidents', icon: FileText, roles: ['psw', 'nurse', 'supervisor', 'executive'] },
    { label: 'Residents', path: '/vision/residents', icon: Users, roles: ['psw', 'nurse', 'supervisor', 'executive'] },
    { label: 'Call Bell', path: '/vision/call-bell', icon: BellRing, roles: ['psw', 'nurse', 'supervisor', 'executive'] },
    { label: 'Call Bell Analytics', path: '/vision/call-bell/analytics', icon: BarChart3, roles: ['supervisor', 'executive'] },
    { label: 'Shift Summary', path: '/vision/shifts', icon: Clock, roles: ['nurse', 'supervisor'] },
    { label: 'Reports', path: '/vision/reports', icon: BarChart3, roles: ['nurse', 'supervisor', 'executive'] },
    { label: 'Dashboard', path: '/vision/dashboard', icon: BarChart3, roles: ['executive'] },
  ],
};

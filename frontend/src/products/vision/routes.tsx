import { Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from '@/platform/router/ProtectedRoute';
import { NurseDashboard } from './pages/nurse/NurseDashboard';
import { NurseAlertView } from './pages/nurse/NurseAlertView';
import { SupervisorDashboard } from './pages/supervisor/SupervisorDashboard';
import { ReviewQueuePage } from './pages/supervisor/ReviewQueuePage';
import { ClipReviewPage } from './pages/supervisor/ClipReviewPage';
import { ExecutiveDashboard } from './pages/executive/ExecutiveDashboard';
import { BoardReportPage } from './pages/executive/BoardReportPage';
import { RoomGridPage } from './pages/shared/RoomGridPage';
import { RoomDetailPage } from './pages/shared/RoomDetailPage';
import { IncidentListPage } from './pages/shared/IncidentListPage';
import { IncidentDetailPage } from './pages/shared/IncidentDetailPage';
import { ResidentsPage } from './pages/shared/ResidentsPage';
import { ShiftSummaryPage } from './pages/shared/ShiftSummaryPage';
import { ReportsPage } from './pages/shared/ReportsPage';
import { CallBellPage } from './pages/shared/CallBellPage';
import { CallBellAnalyticsPage } from './pages/shared/CallBellAnalyticsPage';

export default function VisionRoutes() {
  return (
    <Routes>
      {/* PSW + Nurse + Supervisor: alerts is shared entry point */}
      <Route element={<ProtectedRoute allowedRoles={['psw', 'nurse', 'supervisor']} />}>
        <Route path="alerts" element={<NurseDashboard />} />
        <Route path="alerts/:eventId" element={<NurseAlertView />} />
      </Route>

      {/* Supervisor only */}
      <Route element={<ProtectedRoute allowedRoles={['supervisor']} />}>
        <Route path="review" element={<ReviewQueuePage />} />
        <Route path="clips" element={<ClipReviewPage />} />
      </Route>

      {/* Executive */}
      <Route element={<ProtectedRoute allowedRoles={['executive']} />}>
        <Route path="dashboard" element={<ExecutiveDashboard />} />
        <Route path="board-report" element={<BoardReportPage />} />
      </Route>

      {/* Call Bell Analytics - supervisor/executive */}
      <Route element={<ProtectedRoute allowedRoles={['supervisor', 'executive']} />}>
        <Route path="call-bell/analytics" element={<CallBellAnalyticsPage />} />
      </Route>

      {/* Shared (all authenticated roles) */}
      <Route path="call-bell" element={<CallBellPage />} />
      <Route path="rooms" element={<RoomGridPage />} />
      <Route path="rooms/:roomId" element={<RoomDetailPage />} />
      <Route path="incidents" element={<IncidentListPage />} />
      <Route path="incidents/:incidentId" element={<IncidentDetailPage />} />
      <Route path="residents" element={<ResidentsPage />} />
      <Route path="shifts" element={<ShiftSummaryPage />} />
      <Route path="reports" element={<ReportsPage />} />
    </Routes>
  );
}

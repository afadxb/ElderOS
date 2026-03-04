export const ROUTES = {
  LOGIN: '/login',

  // Vision product routes
  VISION_ALERTS: '/vision/alerts',
  VISION_ALERT_DETAIL: '/vision/alerts/:eventId',
  VISION_ROOMS: '/vision/rooms',
  VISION_ROOM_DETAIL: '/vision/rooms/:roomId',
  VISION_REVIEW: '/vision/review',
  VISION_CLIPS: '/vision/clips',
  VISION_INCIDENTS: '/vision/incidents',
  VISION_INCIDENT_DETAIL: '/vision/incidents/:incidentId',
  VISION_RESIDENTS: '/vision/residents',
  VISION_SHIFTS: '/vision/shifts',
  VISION_REPORTS: '/vision/reports',
  VISION_DASHBOARD: '/vision/dashboard',
  VISION_BOARD_REPORT: '/vision/board-report',

  // Call Bell routes
  VISION_CALL_BELL: '/vision/call-bell',
  VISION_CALL_BELL_ANALYTICS: '/vision/call-bell/analytics',

  // Platform routes
  SYSTEM_HEALTH: '/system',
  SETTINGS: '/settings',
} as const;

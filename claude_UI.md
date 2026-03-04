# CLAUDE.md — ElderOS Vision (Modern SaaS Dashboard + Responsive Web App UI)

You are designing a modern, enterprise-grade SaaS UI for **ElderOS Vision**: an on-prem, edge AI room safety system for long-term care (LTC). The product detects falls/bed-exits/inactivity, alerts staff in seconds, and auto-generates incident documentation and audit trails. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

## Non-negotiables (product truth)
- Deployment: **stand-alone, on-prem edge** (no EHR integration in Phase 1). :contentReference[oaicite:2]{index=2}
- Core loop: **Detect → Alert → Document → Follow-up**. :contentReference[oaicite:3]{index=3}
- Privacy-first: no facial recognition, no audio, bathroom exclusion zones, role-based clip access with audit logging. :contentReference[oaicite:4]{index=4}
- Alerting: confidence tiers (high=immediate, medium=review queue, low=logged), escalation chain, and **two-step tracking**: Acknowledge vs Resolve. :contentReference[oaicite:5]{index=5}
- System health monitoring is first-class (camera heartbeat, latency, disk, NTP drift). :contentReference[oaicite:6]{index=6}

## Design target
Modern SaaS feel (clean, fast, responsive) while still **clinical/operational**:
- Card + table + timeline patterns (not playful “startup” styling)
- High legibility, strong hierarchy, restrained color
- Color is semantic only: blue=actions, red=critical, amber=warning, green=ok/completed
- Works on: nurse station tablet + mobile browser + supervisor desktop. :contentReference[oaicite:7]{index=7}

## Roles and navigation (must implement)
- Nurse (mobile-first): emergency-first UX; one-thumb acknowledge. :contentReference[oaicite:8]{index=8}
- Supervisor (tablet/desktop): shift view, review queue, exports, risk ranking. :contentReference[oaicite:9]{index=9}
- Executive (desktop): monthly trends, board-ready reporting. :contentReference[oaicite:10]{index=10}
- IT Admin: system health, cameras, storage, NTP, updates.

Navigation model:
- Left sidebar on desktop/tablet (collapsible)
- Bottom nav on mobile (Nurse)
Primary sections:
1) Live Alerts
2) Room Grid
3) Review Queue
4) Incidents
5) Residents/Risk
6) Shift Summary
7) Reports (Weekly Digest, Trends)
8) System Health
9) Settings (Zones/Retention/Alert Rules/Roles)

## Required pages (generate all, responsive)
### 1) Nurse View (mobile-first, primary)
- Full-screen alert card: Room # huge, resident ID/name, event type, timer, **Acknowledge** primary CTA
- Swipe/next pattern: “Recent events” for that resident/room with minimal navigation (no complex menus during emergencies). :contentReference[oaicite:11]{index=11}
- Room grid (glanceable): green/yellow/red statuses; tap opens room detail
- High-risk list with fall risk score + trend arrow (observe-only mode supported). :contentReference[oaicite:12]{index=12}

### 2) Supervisor Dashboard
- Shift overview: events, unacknowledged alerts, response times
- Review Queue for medium-confidence events (triage + dismiss/confirm)
- Incident export: one-click PDF export
- Clip request/review flow with explicit access logging (audit trail). :contentReference[oaicite:13]{index=13}

### 3) Executive Dashboard
- Trends: falls/month, unwitnessed fall rate, avg response time
- Unit-by-unit, shift-by-shift comparisons
- Liability exposure indicators: slow responses, unacknowledged alerts
- Print-ready “Board Report” view. :contentReference[oaicite:14]{index=14}

### 4) Incident Detail (defensible record)
Must display:
- NTP timestamp
- pre-event summary, post-event state
- ack time, resolve time, escalation timeline
- repeat-fall indicator
- “Download Incident PDF” :contentReference[oaicite:15]{index=15}

### 5) System Health
- Camera heartbeat per room (last seen)
- Inference latency vs baseline
- Disk usage + retention policy + auto-purge thresholds
- NTP drift status
- Nightly self-test report view :contentReference[oaicite:16]{index=16}

### 6) Settings
- Alert escalation rules (2 min → supervisor SMS, etc.)
- Confidence thresholds (high/med/low)
- Retention (3–14 days)
- Exclusion zones (bathroom)
- Roles/permissions (nurse/supervisor/executive/IT) :contentReference[oaicite:17]{index=17}

## Data visualization requirements
- “Live” alert timeline (last 60 minutes)
- Response time distribution (median + outliers)
- Risk score trends (per resident and facility)
- Room heatmap (“problem rooms”) :contentReference[oaicite:18]{index=18}

## Copy rules
- Operational, direct, no cheerleading
Examples:
- “Fall detected — Room 214”
- “Acknowledge to stop escalation”
- “Resolved at 02:14”
- “Camera offline (last heartbeat 8m ago)”

## Output format (always)
Return in this exact order:
1) Information architecture + key user flows (Nurse/Supervisor/Executive/IT)
2) Page-by-page UI spec (Desktop/Tablet/Mobile) with layout details
3) Component inventory + design tokens
4) Production-ready frontend code scaffold:
   - React + TypeScript
   - TailwindCSS
   - Chart lib (Recharts or Chart.js)
   - Mock data generator aligned to ElderOS concepts
   - Role-based routes and navigation
   - A11y: keyboard nav, focus states, ARIA labels

## Component system (minimum)
- AppShell (Sidebar/Topbar)
- MobileBottomNav (Nurse)
- AlertCard (critical + countdown)
- RoomStatusGrid
- IncidentTimeline
- ResponseTimeBadge (ack/resolve)
- RiskScoreCard (trend)
- ReviewQueueTable
- HealthStatusTable
- PDFExportButton (stub)
- PermissionGate (RBAC)

## Make assumptions, do not ask questions
If any details are missing, choose the most operationally sensible default aligned to LTC workflows and the Phase 1 scope (room safety + alerts + documentation + reporting). :contentReference[oaicite:19]{index=19}

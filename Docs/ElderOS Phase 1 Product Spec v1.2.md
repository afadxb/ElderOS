# ElderOS Vision

## Phase 1 Product Specification

### Room-Based AI Safety System for Long-Term Care

---

| Field | Value |
|-------|-------|
| Document Version | 1.2 — Revised with PSW Role, Dual-Sensor Architecture, Call Bell Integration |
| Classification | Confidential |
| Deployment Model | Stand-alone, on-prem edge system (no EHR integration) |
| Primary Buyer | Long-Term Care (LTC) Homes, Retirement Homes |
| Primary Objective | Reduce unwitnessed falls, improve response time, create defensible incident documentation |

---

## 1. Executive Summary

ElderOS Vision is an AI-powered edge-processing safety system installed inside resident rooms in long-term care facilities. It continuously analyzes human movement and behavior patterns to detect falls, unsafe transfers, bed exits, and prolonged inactivity — without wearables and without requiring nurse documentation to operate.

The system processes video and sensor data locally on-premise and outputs events, alerts, and compliance records — not surveillance video. Phase 1 is intentionally narrow: room safety, automated documentation, proactive risk flagging, and call bell response tracking. This is a safety appliance, not a clinical platform.

**Operating Principle: DETECT → ALERT → DOCUMENT → FOLLOW-UP**

### 1.1 What This Product Actually Sells

The core value proposition is liability defense and insurance cost reduction, delivered through measurable resident safety improvements. LTC administrators purchase risk reduction with minimal staff disruption. The automated incident documentation is the primary sales weapon — every administrator has experienced a lawsuit or near-miss where documentation was incomplete.

Phase 1 includes call bell integration as a secondary value driver — response time accountability is a persistent compliance gap in LTC, and call bell data provides immediate, measurable performance metrics without waiting for AI calibration.

Phase 1 explicitly excludes: EHR integration, vitals monitoring, medication tracking, staff scheduling, wearables, facility-wide RTLS tracking, and predictive hospital analytics. Those belong to Phase 2 (CareIQ).

---

## 2. System Overview

### 2.1 Core Detection Capabilities

The system provides the following detection modules, prioritized by implementation order and reliability confidence:

| Tier | Module | Detects | Output |
|------|--------|---------|--------|
| Tier 1 | Real-Time Fall Detection | Floor impact, uncontrolled descent, lying on floor beyond threshold | Alert within 3-6 seconds with room ID, resident ID, timestamp |
| Tier 1 | Bed Exit Monitoring | Sitting on bed edge, standing from bed, night bed exit (configurable hours) | Pre-fall intervention alerts, prolonged edge-of-bed warnings |
| Tier 2 | Unsafe Transfer Detection | Unassisted standing, wheelchair exit, instability during transfer | Real-time alert to floor staff. Replaces pressure mats and chair alarms |
| Tier 2 | Prolonged Inactivity | No movement beyond configured time, potential unconsciousness | Escalating alert based on inactivity duration |
| Tier 3 | Night Wandering | Multiple nighttime exits, pacing behavior | Pattern reporting to supervisor (not real-time alerting) |

Recommendation: "Confusion patterns" and "chair slip" detection are deferred from Phase 1. Confusion pattern analysis is a research-grade problem that will generate excessive false positives and erode staff trust. Chair slip from a ceiling-mounted wide-angle camera lacks sufficient accuracy for production use.

### 2.2 Dual-Sensor Architecture

Rooms can be equipped with one or both sensor types:

| Sensor Type | Technology | Strengths | Limitations |
|-------------|-----------|-----------|-------------|
| **AI Vision** | 4MP PoE IR Camera + pose estimation | Highest accuracy for fall/transfer detection, visual context for incident review | Privacy sensitivity, requires exclusion zones |
| **AI Sensor** | mmWave radar (60GHz) | Privacy-friendly (no video), works through blankets/bedding, no light needed | Lower spatial resolution, no visual incident context |
| **Hybrid** | Both AI Vision + AI Sensor | Fused confidence scoring, redundancy, best accuracy | Higher per-room cost, more complex installation |

Each room is configured as one of three sensor types: `AI Vision`, `AI Sensor`, or `Hybrid`. The system UI displays the sensor type for every room on the room grid, so staff know the detection capability per room at a glance.

When both sensors detect an event simultaneously, confidence scores are fused — producing higher-confidence alerts that reduce false positives. Hybrid rooms can achieve >95% detection accuracy.

Sensor source is recorded on every event: `AI Vision`, `AI Sensor`, or `Fused` (when both contributed to the detection).

### 2.3 Resident Mobility Profile (Automatic Risk Assessment)

The system continuously builds a behavioral baseline per resident without manual assessment forms.

Metrics tracked:
- Walking speed and gait regularity
- Transfer stability (sit-to-stand consistency)
- Time upright per day
- Nighttime activity frequency
- Frequency of assistance-free movement

Output: Daily Fall Risk Score (0-100) with flags for rapid deterioration, increasing instability, and elevated fall probability. Risk scoring launches in observe-only mode during Phase 1A and activates in Phase 1B after baseline calibration.

---

## 3. Hardware Architecture

Per 25-room unit (typical deployment):

| Component | Specification | Notes |
|-----------|---------------|-------|
| Edge AI Appliance | NVIDIA Jetson Orin NX (8GB+) | Upgraded from Orin Nano. Nano's 1024-core GPU and 8GB RAM is too tight for 25 concurrent pose estimation streams. NX provides necessary headroom for ~$150 additional cost. |
| Operating System | Ubuntu LTS + Docker runtime | Container-based deployment for reproducible updates |
| Storage | Local SSD 1TB (encrypted) | AES-256 at rest. Self-monitoring for capacity alerts. |
| AI Vision Sensors | 4MP PoE IR, 2.8mm lens (wide FOV), 1 per room | Ceiling or upper wall mount. Night vision required. No audio recording. Hikvision or Dahua recommended (ONVIF/RTSP standard). |
| AI Sensors (Radar) | 60GHz mmWave radar modules | Wall-mount at 1.2-1.5m height. No privacy concerns. Through-blanket detection. |
| Network | VLAN isolated, local LAN only | No cloud dependency for operation. Outbound-only optional for remote support. |
| Call Bell Interface | Serial/TCP bridge to nurse call system | Integration with Jeron, Rauland, or Hill-Rom nurse call systems. See Section 8. |

Critical: Night vision IR quality varies wildly between camera models. Cheap IR cameras wash out at close range and lose detail at distance. Specific camera models must be tested in actual LTC rooms at night before committing to the hardware BOM.

### 3.1 Camera Placement Requirements

Camera placement is an art, not a specification line item. A 2.8mm lens ceiling-mounted in a room with a hospital bed, wheelchair, side table, and bathroom door creates significant occlusion zones. The deployment package must include:

- Room-type diagrams with mounting positions (standard single, standard double, corner room)
- Explicit exclusion zones (do not mount directly above bed, avoid backlight from windows)
- Field-of-view validation checklist per room
- Bathroom exclusion zone configuration

Optional for Phase 1.5 (not required for launch): corridor cameras, nurse station display screen.

---

## 4. Software Architecture

### 4.1 Edge Processing Stack

| Layer | Function | Technology |
|-------|----------|------------|
| Video Ingestion | RTSP stream capture at 3-5 fps (not full rate) | GStreamer + NVIDIA DeepStream |
| Radar Ingestion | mmWave point cloud processing | Custom radar SDK integration |
| Person Detection | Identify and localize humans in frame | YOLOv8-nano or RT-DETR-lite (TensorRT optimized) |
| Pose Estimation | Skeletal keypoint extraction for body position | RTMPose-m (MMPose, TensorRT compatible) |
| Sensor Fusion | Combine AI Vision + AI Sensor confidence scores | Weighted fusion algorithm (hybrid rooms only) |
| Event Engine | Fall detection, behavior analysis via state machine | Python state machine (custom, rule-based on ML outputs) |
| Alert Engine | Notifications, escalation, acknowledgment tracking | WebSocket (dashboard) + Twilio (SMS fallback) |
| Compliance Engine | Automated incident documentation + audit trail | FastAPI backend + PDF generation |
| Database | Event metadata, risk scores, response timestamps, audit logs | SQLite (single-facility, zero-config, no service to manage) |
| Dashboard | PSW, nurse, supervisor, and executive interfaces | React frontend + FastAPI backend |
| System Health Monitor | Sensor heartbeat, inference latency, disk usage, NTP sync | Custom daemon with alert integration |
| Call Bell Interface | Nurse call system event capture | Serial/TCP middleware (see Section 8) |

All inference is performed locally. No cloud dependency for core operation.

### 4.2 Critical Architecture Decisions

**Frame Sampling**
Process 3-5 fps for monitoring, burst to full frame rate on event trigger. This reduces compute load by 6-10x and allows the Orin NX to handle 25 rooms with headroom. Processing full 30fps per camera is unnecessary and will exceed hardware capacity.

**Rule-Based Event Engine (Not End-to-End ML)**
Pose estimation uses ML. But event classification (e.g., "person on floor for >10 seconds after rapid vertical position change") is implemented as a deterministic state machine applied to ML outputs. This makes the system debuggable, tunable per facility, and eliminates the black-box problem. When a facility reports false alarms, parameters can be adjusted without retraining models.

**Confidence Threshold + Human Review Queue**
Not every event is high-confidence. The system classifies events into three tiers:
- **High confidence (>85%)**: Immediate alert to floor staff
- **Medium confidence (60-85%)**: Queued for async supervisor review within the dashboard (no audible alarm)
- **Low confidence (<60%)**: Logged for pattern analysis, not surfaced in real-time

This structure manages false positive rates without missing real events.

**Video Snippet Access Control**
Short event video clips are retained for incident review. Access requires role-based authorization: PSWs see alert metadata only; supervisors can request clip review; clip access is logged in the audit trail. In PHIPA-regulated environments, open access to video is a compliance risk — every view must be justified and recorded.

---

## 5. System Health Monitoring

If the system is down and a fall occurs, the facility is worse off than having no system — because they will be asked why their safety system was not operational. System self-monitoring is not optional.

| Monitor | Frequency | Action on Failure |
|---------|-----------|-------------------|
| AI Vision sensor heartbeat | Every 60 seconds | Immediate alert to supervisor + dashboard flag on affected room |
| AI Sensor (radar) heartbeat | Every 60 seconds | Same as above. Room marked offline if all sensors down. |
| Inference pipeline latency | Continuous | Alert if latency exceeds 2x baseline (indicates compute bottleneck) |
| Disk usage | Hourly | Alert at 80% capacity; auto-purge oldest non-flagged clips at 90% |
| NTP time sync | Every 15 minutes | Alert if drift exceeds 5 seconds (timestamps are legal evidence) |
| Nightly self-test | Daily at 3:00 AM | Automated diagnostic report emailed to facility IT contact |
| Call bell interface | Every 60 seconds | Alert if nurse call system connection lost |

---

## 6. Alerting and Escalation

### 6.1 Alert Delivery Channels

- Nurse station dashboard (primary — dedicated tablet with persistent audio)
- Mobile browser on staff phones (secondary)
- SMS via Twilio (escalation fallback, facility-controlled)

Design decision: Sound alerts should come from a dedicated tablet at the nurse station, not phones. Phones get silenced. A persistent audio source at the station is more reliable for critical alerts.

### 6.2 Escalation Rules

Configurable per facility. Default escalation chain:

1. PSW alerted immediately (dashboard + audio + mobile push)
2. If not acknowledged within 2 minutes → nurse + supervisor alert via SMS
3. If still unacknowledged within 5 minutes → charge nurse alert
4. All escalation timestamps recorded in incident audit trail

### 6.3 Two-Step Response Tracking

Alert acknowledgment is split into two distinct actions:

1. **Acknowledge**: "I see this alert" — stops escalation, records awareness time
2. **Resolve**: "I have attended to the resident" — records physical response time

This distinction captures true response time for compliance reporting and performance analytics.

---

## 7. Incident Documentation (Critical Compliance Feature)

This is the product's most defensible sales feature. When a fall or safety event occurs, the system automatically generates an incident record without any manual documentation from staff.

### 7.1 Auto-Generated Incident Record Contains

- Exact time of event (NTP-synchronized)
- 30-second pre-event activity summary
- Post-event resident state description
- Alert-to-acknowledgment response time
- Who acknowledged the alert (user ID + role)
- Who physically attended (resolve action timestamp)
- Repeat-fall indicator if applicable
- Sensor source (AI Vision, AI Sensor, or Fused)

This produces a defensible audit timeline. No manual note writing required beyond clinical assessment. This is the primary differentiator in sales conversations.

### 7.2 Post-Fall Automated Workflow

After a detected fall, the system automatically:
1. Creates incident record with full timeline
2. Tags resident as high-risk on dashboard
3. Schedules reassessment reminder (configurable interval)
4. Flags room on supervisor dashboard

Supervisor receives: event summary, response time, repeat fall indicator, and risk score change.

---

## 8. Call Bell Integration (NEW)

### 8.1 Overview

ElderOS integrates with existing nurse call systems (Jeron, Rauland, Hill-Rom) to capture call bell events with precise timestamps. This is not an AI feature — it is a hardware integration that provides immediate value from day one without calibration.

**Operating Principle: PRESSED → RESPONDED → MEASURED**

Call bell response time is one of the most scrutinized metrics in LTC regulatory inspections. Most facilities have no reliable way to measure it. This integration solves that.

### 8.2 Data Captured Per Call Bell Event

| Field | Description |
|-------|-------------|
| Pressed At | Exact timestamp when resident pressed the call bell (NTP-synced) |
| Responded At | Timestamp when staff physically responded/arrived |
| Response Time | Calculated: Responded At - Pressed At (seconds) |
| Responded By | Staff ID and name of responder |
| Room / Resident | Auto-linked from room and resident registry |
| Origin | Bedside, bathroom, hallway, or pendant |
| Priority | Emergency, urgent, or normal (from nurse call system signal) |
| Shift | Day (07:00-15:00), Evening (15:00-23:00), Night (23:00-07:00) |
| Vendor | Jeron, Rauland, or Hill-Rom (one per facility) |

### 8.3 Response Time Thresholds

| Threshold | Time | Meaning |
|-----------|------|---------|
| Good | Under 60 seconds | Staff responded promptly |
| Warning | 60-120 seconds | Acceptable but below target |
| Critical | Over 180 seconds | Compliance risk, requires review |
| Emergency Max | 60 seconds | Emergency calls must be under 60s |
| Compliance Target | 90% under 120s | Facility-wide SLA target |

### 8.4 Analytics Provided

**By Staff**: Average response time, median, fastest/slowest, calls under 60s, calls over 3 minutes. Identifies high-performers and staff needing support. Displayed as a horizontal bar chart with color-coded performance thresholds.

**By Floor/Unit**: Total calls, average response time, peak call hours, breakdown by priority and origin. Identifies units with staffing gaps.

**By Shift**: Day vs Evening vs Night comparison. Total calls, average response, slow responses per shift. Night shift consistently shows slower response — this is expected and should not trigger alarm, but extreme outliers should be flagged.

**30-Day Trend**: Daily call volume and average response time over time. Identifies systemic improvement or degradation.

### 8.5 Integration Architecture

```
Nurse Call System (Jeron/Rauland/Hill-Rom)
    │
    ├── Serial/TCP Interface
    │
    ▼
Call Bell Middleware (on Edge Appliance)
    │
    ├── Event capture: button press → timestamp
    ├── Staff response: badge/acknowledge → timestamp
    │
    ▼
ElderOS Database
    │
    ├── Real-time dashboard (active calls)
    ├── Historical log with filters
    └── Analytics engine (staff/floor/shift breakdowns)
```

### 8.6 Why Call Bell Data Matters for Sales

Call bell response time is:
- **Measurable from day one** — no AI calibration needed
- **Immediately visible to administrators** — clear before/after comparison
- **Regulatory ammunition** — Ontario LTC inspections ask about response times
- **Staff accountability** — individual and shift-level performance data
- **Insurance-relevant** — slow response after a fall call correlates with worse outcomes

This feature alone can justify a meeting with an LTC administrator who is not yet ready to discuss AI.

---

## 9. Facility Management

### 9.1 Administrative Configuration

The system includes an admin-only facility management interface for configuring:

- **Units**: Name, floor assignment (e.g., "Unit A" on Floor 1, "Unit B" on Floor 2)
- **Rooms**: Room number, unit assignment, room type (single or semi-private), sensor type (AI Vision, AI Sensor, or Hybrid)
- **Cascading operations**: Renaming a unit propagates to all rooms and residents. Deleting a unit removes associated rooms, residents, and sensor assignments.

This replaces hardcoded facility configuration and allows non-technical administrators to manage room inventory as residents move, rooms are renovated, or units are reorganized.

### 9.2 Room Types

| Type | Description |
|------|-------------|
| Single | One bed, one resident. Standard monitoring. |
| Semi-Private | Two beds (Zone A / Zone B), two residents. Alerts identify which bed zone triggered the event. |

---

## 10. Dashboard Interfaces

### 10.1 Role Hierarchy

ElderOS uses a 5-role RBAC model reflecting real LTC staffing:

| Role | Label | Home Page | Primary Function |
|------|-------|-----------|-----------------|
| PSW | PSW (Personal Support Worker) | Alerts | First responder. Receives and acknowledges alerts. Mobile-first interface. |
| Nurse | Nurse (RPN/RN) | Alerts | Clinical oversight. All PSW capabilities + incident export, shift summaries, reports. |
| Supervisor | Supervisor | Alerts | Operations management. All nurse capabilities + review queue triage, video clip access, call bell analytics. |
| Executive | Executive | Dashboard | Leadership reporting. Facility-wide trends, board reports, call bell analytics. Read-only. |
| Admin | IT Admin | System Health | Technical administration. System health, settings, facility management. No clinical access. |

**Key design decision**: PSWs are the actual first responders in Canadian LTC — not nurses. The PSW role gets a mobile-first interface with no sidebar navigation, optimized for one-thumb operation while walking. Nurses serve as clinical supervisors with broader analytics access.

### 10.2 PSW View (Mobile-First, Primary Interface)

Design principle: A PSW running down a hallway should be able to acknowledge an alert with one thumb tap on a phone screen.

- Full-screen alert card on event: room number displayed large, one-tap acknowledge button
- Color-coded room grid (green / yellow / red) — glanceable from across the nursing station
- Sensor type indicator on each room tile (AI Vision icon, AI Sensor icon, or both for Hybrid)
- No login required from facility network (session-based, role auto-detected by device)
- Swipe to see resident's recent events — no navigation menus during emergencies
- Call bell log — see active and recent call bell events
- High-risk resident list with current fall risk scores

If the PSW view requires training to use, it has failed. Zero-training operation is a hard requirement.

### 10.3 Nurse View (Mobile + Desktop)

All PSW capabilities plus:
- Shift summary dashboard: events, response times, unacknowledged alerts
- Incident export to PDF
- Reports page with weekly digest and response time analytics
- Call bell log with response time tracking

### 10.4 Supervisor View (Tablet / Desktop)

All nurse capabilities plus:
- Review queue for medium-confidence events requiring triage (confirm/dismiss)
- Video clip review request workflow (access-controlled, audit-logged)
- Resident risk ranking sorted by fall risk score with trend indicators
- **Call Bell Analytics**: Response time by staff, by floor, by shift with charts and tables
- Problem rooms heat map (which rooms generate the most events)
- One-click export of incident reports as PDF

### 10.5 Executive View (Desktop, Monthly Cadence)

- Facility-wide trends: falls per month, average response time, unwitnessed fall rate
- Unit-by-unit and shift-by-shift comparisons
- Liability exposure indicator: unacknowledged alerts, slow response rates
- **Call Bell Analytics**: Same analytics as supervisor view for oversight
- Print-ready format for board reporting

### 10.6 Admin View (Desktop)

- System health monitoring: sensor status, inference latency, disk usage, NTP sync
- Sensor health table with per-device status (online / degraded / offline)
- **Facility management**: Add/edit/remove units, rooms. Configure sensor types per room.
- Settings: Escalation rules, confidence thresholds, retention policies, exclusion zones
- No clinical data access (alerts, incidents, residents)

### 10.7 Navigation Structure

| Nav Item | Accessible By | Description |
|----------|--------------|-------------|
| Alerts | PSW, Nurse, Supervisor | Real-time alert feed with acknowledge/resolve |
| Room Grid | All roles | Color-coded room status with sensor type indicators |
| Review Queue | Supervisor | Medium-confidence events requiring triage |
| Incidents | PSW, Nurse, Supervisor, Executive | Historical incident log with response time tracking |
| Residents | PSW, Nurse, Supervisor, Executive | Resident list with risk scores and fall history |
| Call Bell | PSW, Nurse, Supervisor, Executive | Call bell event log with filters and response times |
| Call Bell Analytics | Supervisor, Executive | Response time breakdowns by staff, floor, shift + trend charts |
| Shift Summary | Nurse, Supervisor | Per-shift handoff data |
| Reports | Nurse, Supervisor, Executive | Weekly digest, trends, response time distribution |
| Dashboard | Executive | Facility-wide KPIs and board report |
| System Health | Admin | Sensor status, system metrics, diagnostics |
| Facility | Admin | Unit/room/floor management |
| Settings | Admin | Escalation rules, thresholds, retention, exclusion zones |

---

## 11. Additional Automation Features

### 11.1 Shift Handoff Summary

Auto-generated summary at each shift change: "Here is what happened overnight per unit." Includes events, unresolved alerts, residents flagged high-risk, and rooms requiring attention. Nurses will rely on this and it drives adoption.

### 11.2 Weekly Facility Digest

Auto-generated PDF emailed to administrators weekly. Contains facility-wide event counts, response time averages, risk score trends, call bell compliance rates, and system health status. Zero-effort reporting drives executive buy-in without requiring dashboard login.

### 11.3 Maintenance Self-Monitoring

Sensor health, disk space, inference latency, and network status monitored continuously. If a sensor goes offline at 2:00 AM, the on-call contact is notified before a fall could go undetected in that room.

---

## 12. Privacy and Compliance Controls

Designed for PHIPA-sensitive environments with a privacy-first architecture.

| Control | Implementation |
|---------|---------------|
| No facial recognition | System identifies pose skeletons only. No biometric data captured or stored. |
| No audio capture | AI Vision sensors selected without microphones. Audio recording explicitly disabled. |
| AI Sensor privacy | Radar sensors capture point clouds only. No visual data whatsoever. Privacy-friendly alternative for sensitive residents. |
| On-device processing | All inference performed locally. No video transmitted off-premise. |
| Video retention | Short event clips only. Configurable retention (3-14 days). Auto-purge on expiry. |
| Anonymization | Face/body silhouette rendering option for demo and review scenarios. |
| Bathroom exclusion | Configurable exclusion zones prevent any processing in bathroom areas. |
| Video access control | Role-based authorization required for clip review. Every access logged in audit trail. |

Recommendation: Prepare a privacy whitepaper before the first sales call. Families and advocacy groups will challenge any camera-in-room system regardless of technical safeguards. A demo mode showing anonymized silhouettes is essential for buyer comfort. Offering AI Sensor (radar-only) rooms as an alternative eliminates the camera objection entirely for high-sensitivity residents.

---

## 13. Data Storage and Security

### 13.1 Local Storage

- Event metadata, risk scores, response timestamps, call bell events, and audit logs stored in SQLite
- Video clips: short event snippets only, retention configurable (3-14 days)
- AES-256 encryption at rest on local SSD
- Automated capacity monitoring with alerts at 80% and auto-purge at 90%

### 13.2 Security Controls

- HTTPS for all dashboard communication
- Role-based access control (PSW, nurse, supervisor, executive, IT admin)
- Complete audit logging of all user actions and data access
- No inbound external access required
- Outbound-only optional connection for remote support and software updates

---

## 14. Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Edge Compute | NVIDIA Jetson Orin NX | Sufficient GPU for 25 streams at 3-5fps with headroom. TensorRT native. |
| Person Detection | YOLOv8-nano / RT-DETR-lite | Optimized for TensorRT on Jetson. Well-documented, active community. |
| Pose Estimation | RTMPose-m (MMPose) | Best accuracy/speed tradeoff for edge. TensorRT compatible. |
| Radar Processing | Custom mmWave SDK | Point cloud processing for AI Sensor rooms. |
| Video Pipeline | GStreamer + DeepStream | NVIDIA's optimized pipeline. Handles RTSP natively with hardware decode. |
| Event Engine | Python state machine (custom) | Debuggable, tunable per facility. Deterministic behavior. |
| Database | SQLite | Simple, zero-config, adequate for single-facility volume. No service to manage. |
| Backend API | FastAPI (Python) | Async, lightweight, same language as ML pipeline. |
| Frontend | React + TypeScript + Tailwind CSS | Standard, maintainable, strong mobile browser support. Component library with shared UI primitives. |
| State Management | Zustand (real-time alerts) + React Query (server state) | Lightweight, minimal boilerplate, automatic cache invalidation. |
| Charts | Recharts | Composable React chart components. Used for response time, trend, and comparison visualizations. |
| Alert Delivery | WebSocket + Twilio SMS | Real-time dashboard + reliable SMS escalation fallback. |
| Call Bell Integration | Serial/TCP middleware | Captures events from Jeron, Rauland, or Hill-Rom nurse call systems. |
| Deployment | Docker Compose on Ubuntu LTS | Reproducible, updatable, standard container orchestration. |
| AI Vision Sensors | Hikvision / Dahua 4MP PoE IR | Commodity, reliable, ONVIF/RTSP standard. Wide availability. |
| AI Sensors (Radar) | 60GHz mmWave modules | Privacy-friendly, through-blanket detection. No video data. |

---

## 15. Implementation Phases

### Phase 1A — Proof of Value (8 Weeks, 1 Unit / 25 Rooms)

Goal: Prove the system detects falls reliably in a real environment.

- Camera + radar sensor installation + edge appliance setup
- Fall detection only (Tier 1 — no other event types yet)
- PSW dashboard with alert + one-tap acknowledge
- Auto-incident record generation
- **Call bell integration active from day one** — immediate measurable value
- 2-week silent monitoring for AI calibration before alert activation

Success metrics:
- Detect falls faster than staff with <5% false positive rate per shift
- Call bell response time baseline established within first week

Critical: Do not deploy all event types on day one. False positives from less-mature detections (transfers, inactivity) will destroy PSW trust in fall alerts, which are the most important feature. Ship falls first. Prove reliability. Then expand. Call bell tracking provides immediate wins while AI calibrates.

### Phase 1B — Full Feature Set (6 Weeks After 1A)

Goal: Expand detection capabilities and analytics after trust is established.

- Add bed exit monitoring (Tier 1)
- Add unsafe transfer detection (Tier 2)
- Add prolonged inactivity monitoring (Tier 2)
- Activate escalation chains
- Launch supervisor analytics view (including call bell analytics)
- Risk scoring baseline activated (observe-only → active)
- Nurse role enabled with shift summaries and reports access

### Phase 1C — Operational Maturity (4 Weeks After 1B)

Goal: Facility operates independently with full self-service.

- Daily risk scores active with trend alerts
- Executive dashboard launched with call bell analytics
- PDF incident report export
- Shift handoff summaries and weekly digest emails (includes call bell compliance)
- System health self-monitoring fully operational
- Facility management admin interface active
- Facility staff fully self-sufficient (no vendor support for daily operation)

### Installation Workflow (Per Unit)

| Week | Activity |
|------|----------|
| Week 1 | Mount sensors (AI Vision + AI Sensor per room config), install edge appliance, connect call bell interface, configure detection zones and exclusion areas |
| Week 2 | Silent monitoring and calibration. AI system runs but does not alert staff. Call bell tracking active (immediate value). Baseline data collection. |
| Week 3 | Activate AI alerts. Brief floor staff on dashboard (15-minute walkthrough, not formal training). |

---

## 16. Remote Update Strategy

"No cloud dependency" is correct for operation but creates a critical update problem. Pushing model updates, bug fixes, and configuration changes to 50+ facilities requires planning now, even if the mechanism is not built in Phase 1A.

Recommended Approach:
- Lightweight remote management agent (outbound-only, facility-approved)
- Docker container pull from private registry on schedule or manual trigger
- Facility IT must approve update policy during installation
- Rollback capability: previous container version retained for instant revert
- Update verification: automated self-test after update confirms pipeline is functional

Without this, every software update requires a technician on-site. This becomes unsustainable beyond 10 facilities.

---

## 17. Staff Adoption Strategy

Staff resistance will kill this product faster than any technical issue. The spec must address what changes for PSWs and nurses explicitly.

### 17.1 What Changes for PSWs (Primary Users)

- **Added**: Audio/visual alerts when a resident event is detected. One-tap acknowledge on phone or station tablet. Call bell response tracking (staff are identified when responding).
- **Removed**: Manual incident report writing for detected events (auto-generated). Pressure mat and chair alarm management.
- **Unchanged**: All clinical assessment, direct care, and treatment decisions remain with nursing staff.

### 17.2 What Changes for Nurses

- **Added**: Shift summaries auto-generated. Incident export with complete timelines. Call bell response oversight.
- **Removed**: Manual documentation of fall events. Manual compilation of shift handoff notes.
- **Unchanged**: Clinical decision-making, medication management, care planning.

### 17.3 Adoption Risks and Mitigations

- **"Big Brother" perception**: Address directly during installation. Show anonymized silhouette mode. Offer AI Sensor (radar-only) rooms for sensitive cases. Emphasize the system monitors for safety, not performance. Call bell response tracking should be framed as "supporting fair workload distribution" not "surveillance."
- **Alert fatigue**: Managed through confidence tiers and per-facility tuning. Phased rollout prevents alert overload on day one.
- **"More work" perception**: Demonstrate that acknowledgment takes one tap. Auto-documentation removes paperwork. Net reduction in staff workload.
- **Call bell accountability resistance**: Staff may resist being individually tracked. Frame as facility-wide improvement tool. Show aggregate shift data before individual data. Lead with "How can we help the night shift?" not "Who is slowest?"

---

## 18. Acceptance Criteria

The product is considered successful when a facility can demonstrate all five outcomes:

| # | Outcome | Measurement | Target |
|---|---------|-------------|--------|
| 1 | Faster fall response time | Alert-to-physical-attendance time | <3 minutes average across all shifts |
| 2 | Reduction in unwitnessed falls | Percentage of falls with system alert before staff discovery | >80% of falls detected by system first |
| 3 | Complete incident documentation | Percentage of events with full auto-generated audit trail | 100% of detected events documented |
| 4 | Ongoing risk monitoring | Daily risk scores generated for monitored residents | Risk scores for all residents by Phase 1C |
| 5 | Call bell compliance | Percentage of call bells answered within 2 minutes | >90% facility-wide |

If these five outcomes are achieved, the facility has measurable risk reduction — which is what they actually purchase.

---

## 19. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| False positive alert fatigue | Critical | Confidence tiers, phased feature rollout, per-facility tuning budget. 5 false alarms per shift = staff ignore all alerts. |
| Compute capacity on edge device | High | Orin NX (not Nano) provides headroom. Frame sampling at 3-5fps reduces load. Monitor utilization from day one. |
| Camera placement / occlusion | High | Room-type installation playbook with diagrams. FOV validation checklist per room. Missed fall due to bad placement is product-killing. |
| Night vision IR quality | High | Test specific camera models in actual LTC rooms at night before committing to BOM. IR washout at close range is common in cheap cameras. |
| Privacy / advocacy pushback | Medium | Privacy whitepaper ready before first sales call. Anonymized silhouette demo mode. AI Sensor (radar) option for sensitive residents. Proactive family communication template. |
| Software update at scale | Medium | Design remote update agent architecture now. Build in Phase 1B. Without it, every update requires on-site technician. |
| Support burden at scale | Medium | LTC facilities have minimal IT. Every offline sensor = support ticket. Remote monitoring of every deployed unit is essential by facility #10. |
| Staff adoption resistance | Medium | Clear "what changes" communication per role. Show net workload reduction. Zero-training interface. Address surveillance perception proactively. |
| Call bell integration compatibility | Medium | Three major vendors (Jeron, Rauland, Hill-Rom) cover >80% of installed base. Vendor-specific serial protocol adapters needed. Test integration before each facility deployment. |
| Call bell response tracking resistance | Low | Frame as facility improvement, not individual surveillance. Show aggregate data first. Allow opt-in period before naming individuals. |

---

## Appendix A: Sensor Type Summary

| Configuration | Per-Room Hardware | Detection Quality | Privacy Level | Cost |
|---------------|------------------|-------------------|---------------|------|
| AI Vision Only | 1x 4MP PoE IR camera | Highest (visual + pose estimation) | Medium (video processed locally, exclusion zones required) | $ |
| AI Sensor Only | 1x 60GHz mmWave radar | Good (motion + position, no visual) | Highest (no video, no images) | $ |
| Hybrid | 1x camera + 1x radar | Best (fused confidence scoring) | Medium (same as AI Vision) | $$ |

## Appendix B: Permission Matrix

| Permission | PSW | Nurse | Supervisor | Executive | Admin |
|-----------|-----|-------|------------|-----------|-------|
| View/acknowledge/resolve alerts | Yes | Yes | Yes | - | View only |
| View room grid | Yes | Yes | Yes | Yes | Yes |
| View incidents | Yes | Yes | Yes | Yes | Yes |
| Export incidents | - | Yes | Yes | Yes | - |
| Review queue triage | - | - | Yes | - | - |
| Request/view clips | - | - | Yes | - | - |
| View residents | Yes | Yes | Yes | Yes | - |
| View call bell log | Yes | Yes | Yes | Yes | - |
| Respond to call bells | Yes | Yes | Yes | - | - |
| View call bell analytics | - | - | Yes | Yes | - |
| View shift summary | - | Yes | Yes | - | - |
| View reports | - | Yes | Yes | Yes | - |
| View board report | - | - | - | Yes | - |
| View system health | - | - | - | - | Yes |
| Manage settings | - | - | - | - | Yes |
| Manage facility | - | - | - | - | Yes |

---

*Document Version 1.2 — Updated to reflect dual-sensor architecture (AI Vision + AI Sensor), 5-role RBAC (PSW/Nurse/Supervisor/Executive/Admin), call bell integration (Jeron/Rauland/Hill-Rom), and facility management capabilities.*

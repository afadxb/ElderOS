import type { Room, Resident, AlertEvent, Incident, SensorHealth, SystemMetrics, EscalationRule, ConfidenceThresholds, RetentionPolicy, ExclusionZone, ShiftSummary, Unit, CallBellEvent, Device } from '@/types';

export interface MockStoreState {
  units: Unit[];
  rooms: Room[];
  residents: Resident[];
  events: AlertEvent[];
  incidents: Incident[];
  sensors: SensorHealth[];
  devices: Device[];
  systemMetrics: SystemMetrics;
  shiftSummaries: ShiftSummary[];
  callBellEvents: CallBellEvent[];
  settings: {
    escalationRules: EscalationRule[];
    confidenceThresholds: ConfidenceThresholds;
    retention: RetentionPolicy;
    exclusionZones: ExclusionZone[];
  };
}

class MockStore {
  private state: MockStoreState;

  constructor() {
    this.state = {
      units: [],
      rooms: [],
      residents: [],
      events: [],
      incidents: [],
      sensors: [],
      devices: [],
      systemMetrics: {
        cpuUsage: 35,
        memoryUsage: 52,
        diskUsagePercent: 45,
        diskUsedGB: 450,
        diskTotalGB: 1000,
        retentionDays: 7,
        autoPurgeThresholdPercent: 90,
        ntpDriftMs: 2,
        ntpSyncStatus: 'synced',
        lastSelfTestAt: new Date().toISOString(),
        selfTestPassed: true,
        edgeDeviceUptime: '14d 6h 32m',
      },
      shiftSummaries: [],
      callBellEvents: [],
      settings: {
        escalationRules: [],
        confidenceThresholds: { highMin: 85, mediumMin: 60, lowMin: 30 },
        retention: { clipRetentionDays: 7, metadataRetentionDays: 90, autoPurgeEnabled: true, purgeThresholdPercent: 90 },
        exclusionZones: [],
      },
    };
  }

  get units() { return this.state.units; }
  set units(val: Unit[]) { this.state.units = val; }

  get rooms() { return this.state.rooms; }
  set rooms(val: Room[]) { this.state.rooms = val; }

  get residents() { return this.state.residents; }
  set residents(val: Resident[]) { this.state.residents = val; }

  get events() { return this.state.events; }
  set events(val: AlertEvent[]) { this.state.events = val; }

  get incidents() { return this.state.incidents; }
  set incidents(val: Incident[]) { this.state.incidents = val; }

  get sensors() { return this.state.sensors; }
  set sensors(val: SensorHealth[]) { this.state.sensors = val; }

  /** @deprecated Use sensors instead */
  get cameras() { return this.state.sensors; }
  set cameras(val: SensorHealth[]) { this.state.sensors = val; }

  get systemMetrics() { return this.state.systemMetrics; }
  set systemMetrics(val: SystemMetrics) { this.state.systemMetrics = val; }

  get shiftSummaries() { return this.state.shiftSummaries; }
  set shiftSummaries(val: ShiftSummary[]) { this.state.shiftSummaries = val; }

  get callBellEvents() { return this.state.callBellEvents; }
  set callBellEvents(val: CallBellEvent[]) { this.state.callBellEvents = val; }

  get devices() { return this.state.devices; }
  set devices(val: Device[]) { this.state.devices = val; }

  get settings() { return this.state.settings; }

  acknowledgeEvent(eventId: string, userId: string): AlertEvent | undefined {
    const event = this.state.events.find(e => e.id === eventId);
    if (event && event.status === 'active') {
      event.status = 'acknowledged';
      event.acknowledgedAt = new Date().toISOString();
      event.acknowledgedBy = userId;
      const room = this.state.rooms.find(r => r.id === event.roomId);
      if (room) {
        room.status = 'attention';
        room.statusColor = 'yellow';
      }
    }
    return event;
  }

  resolveEvent(eventId: string, userId: string): AlertEvent | undefined {
    const event = this.state.events.find(e => e.id === eventId);
    if (event && (event.status === 'acknowledged' || event.status === 'active')) {
      event.status = 'resolved';
      event.resolvedAt = new Date().toISOString();
      event.resolvedBy = userId;
      const room = this.state.rooms.find(r => r.id === event.roomId);
      if (room) {
        const otherActive = this.state.events.some(
          e => e.roomId === room.id && e.id !== eventId && (e.status === 'active' || e.status === 'acknowledged')
        );
        if (!otherActive) {
          room.status = 'clear';
          room.statusColor = 'green';
        }
      }
    }
    return event;
  }

  addEvent(event: AlertEvent): void {
    this.state.events.unshift(event);
    const room = this.state.rooms.find(r => r.id === event.roomId);
    if (room) {
      room.status = 'active-alert';
      room.statusColor = 'red';
      room.lastEventAt = event.detectedAt;
    }
  }

  triageReviewItem(eventId: string, action: 'confirm' | 'dismiss'): void {
    const event = this.state.events.find(e => e.id === eventId);
    if (event) {
      event.status = action === 'confirm' ? 'active' : 'dismissed';
    }
  }

  getActiveAlerts(): AlertEvent[] {
    return this.state.events.filter(e => e.status === 'active' || e.status === 'escalated');
  }

  getReviewQueue(): AlertEvent[] {
    return this.state.events.filter(e => e.confidence === 'medium' && e.status === 'active');
  }

  addUnit(unit: Unit): void {
    this.state.units.push(unit);
  }

  updateUnit(id: string, name: string, floor: number): void {
    const unit = this.state.units.find(u => u.id === id);
    if (!unit) return;
    const oldName = unit.name;
    const oldFloor = unit.floor;
    unit.name = name;
    unit.floor = floor;
    // Propagate name/floor changes to rooms
    for (const room of this.state.rooms) {
      if (room.unit === oldName) {
        room.unit = name;
        room.floor = floor;
      }
    }
    // Propagate unit name to residents
    for (const resident of this.state.residents) {
      if (resident.unit === oldName) {
        resident.unit = name;
      }
    }
  }

  removeUnit(id: string): void {
    const unit = this.state.units.find(u => u.id === id);
    if (!unit) return;
    // Remove rooms belonging to this unit
    const roomIds = this.state.rooms.filter(r => r.unit === unit.name).map(r => r.id);
    this.state.rooms = this.state.rooms.filter(r => r.unit !== unit.name);
    // Remove residents in those rooms
    this.state.residents = this.state.residents.filter(r => !roomIds.includes(r.roomId));
    // Remove sensors for those rooms
    this.state.sensors = this.state.sensors.filter(s => !roomIds.includes(s.roomId));
    // Remove unit
    this.state.units = this.state.units.filter(u => u.id !== id);
  }

  addRoom(room: Room): void {
    this.state.rooms.push(room);
  }

  updateRoom(id: string, updates: Partial<Pick<Room, 'number' | 'roomType' | 'sensorType' | 'unit' | 'floor'>>): void {
    const room = this.state.rooms.find(r => r.id === id);
    if (!room) return;
    Object.assign(room, updates);
  }

  removeRoom(id: string): void {
    // Unlink residents
    this.state.residents = this.state.residents.filter(r => r.roomId !== id);
    // Remove sensors
    this.state.sensors = this.state.sensors.filter(s => s.roomId !== id);
    // Remove room
    this.state.rooms = this.state.rooms.filter(r => r.id !== id);
  }

  // Call Bell methods
  respondToCallBell(eventId: string, userId: string, userName: string): CallBellEvent | undefined {
    const event = this.state.callBellEvents.find(e => e.id === eventId);
    if (event && event.status === 'active') {
      event.status = 'responded';
      event.respondedAt = new Date().toISOString();
      event.respondedBy = userId;
      event.respondedByName = userName;
      event.responseTimeSeconds = Math.round(
        (new Date(event.respondedAt).getTime() - new Date(event.pressedAt).getTime()) / 1000
      );
    }
    return event;
  }

  closeCallBell(eventId: string): CallBellEvent | undefined {
    const event = this.state.callBellEvents.find(e => e.id === eventId);
    if (event && event.status === 'responded') {
      event.status = 'closed';
      event.closedAt = new Date().toISOString();
    }
    return event;
  }

  getActiveCallBells(): CallBellEvent[] {
    return this.state.callBellEvents.filter(e => e.status === 'active' || e.status === 'responded');
  }

  // Device management methods
  addDevice(device: Device): void {
    this.state.devices.push(device);
  }

  updateDevice(id: string, updates: Partial<Device>): void {
    const device = this.state.devices.find(d => d.id === id);
    if (!device) return;
    Object.assign(device, updates);
  }

  removeDevice(id: string): void {
    this.state.devices = this.state.devices.filter(d => d.id !== id);
  }
}

export const mockStore = new MockStore();

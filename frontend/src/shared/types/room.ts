export type RoomStatus = 'clear' | 'active-alert' | 'attention' | 'offline';
export type RoomStatusColor = 'green' | 'yellow' | 'red' | 'gray';
export type SensorType = 'ai-vision' | 'ai-sensor' | 'hybrid';
export type RoomType = 'single' | 'semi-private';

export interface RoomResident {
  residentId: string;
  residentName: string;
  bedZone: 'A' | 'B' | null;
}

export interface SensorStatus {
  id: string;
  type: 'ai-vision' | 'ai-sensor';
  online: boolean;
  lastHeartbeat: string;
  healthScore: number;
}

export interface Room {
  id: string;
  number: string;
  unit: string;
  floor: number;
  roomType: RoomType;
  sensorType: SensorType;
  status: RoomStatus;
  statusColor: RoomStatusColor;
  residents: RoomResident[];
  sensors: SensorStatus[];
  lastEventAt: string | null;
  hasExclusionZone: boolean;
}

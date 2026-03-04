import type { Room, AlertEvent } from '@/types';
import { Card, CardHeader, CardTitle, CardContent, Badge, StatusDot } from '@/components/ui';
import { RelativeTime } from '@/components/common/RelativeTime';
import { Shield, Camera, Radio } from 'lucide-react';

interface RoomDetailPanelProps {
  room: Room;
  events: AlertEvent[];
}

const sensorTypeLabels = {
  'ai-vision': 'AI Vision',
  'ai-sensor': 'AI Sensor',
  hybrid: 'AI Vision + AI Sensor',
};

export function RoomDetailPanel({ room, events }: RoomDetailPanelProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Room {room.number}</CardTitle>
          <div className="flex items-center gap-2">
            {room.roomType === 'semi-private' && (
              <Badge variant="default">Semi-Private</Badge>
            )}
            <Badge variant={room.status === 'clear' ? 'success' : room.status === 'active-alert' ? 'critical' : room.status === 'attention' ? 'warning' : 'default'}>
              {room.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-elder-text-secondary">Unit</span>
              <span className="font-medium">{room.unit}</span>
            </div>

            {room.residents.length === 0 ? (
              <div className="flex items-center justify-between text-sm">
                <span className="text-elder-text-secondary">Resident</span>
                <span className="font-medium text-elder-text-muted">Unoccupied</span>
              </div>
            ) : (
              room.residents.map((res) => (
                <div key={res.residentId} className="flex items-center justify-between text-sm">
                  <span className="text-elder-text-secondary">
                    {res.bedZone ? `Bed ${res.bedZone}` : 'Resident'}
                  </span>
                  <span className="font-medium">{res.residentName}</span>
                </div>
              ))
            )}

            <div className="flex items-center justify-between text-sm">
              <span className="text-elder-text-secondary">Sensor</span>
              <div className="flex items-center gap-1.5">
                {room.sensorType === 'ai-sensor' || room.sensorType === 'hybrid' ? (
                  <Radio className="h-3.5 w-3.5 text-elder-text-secondary" />
                ) : (
                  <Camera className="h-3.5 w-3.5 text-elder-text-secondary" />
                )}
                <span className="font-medium">{sensorTypeLabels[room.sensorType]}</span>
              </div>
            </div>

            {room.sensors.map((sensor) => (
              <div key={sensor.id} className="flex items-center justify-between text-sm pl-2">
                <span className="text-elder-text-secondary capitalize">{sensor.type}</span>
                <div className="flex items-center gap-1.5">
                  <StatusDot color={sensor.online ? 'green' : 'red'} />
                  <span className="font-medium">{sensor.online ? 'Online' : 'Offline'}</span>
                </div>
              </div>
            ))}

            {room.hasExclusionZone && (
              <div className="flex items-center gap-1.5 text-sm text-elder-text-secondary">
                <Shield className="h-4 w-4" />
                <span>Bathroom exclusion zone active</span>
              </div>
            )}
            {room.lastEventAt && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-elder-text-secondary">Last event</span>
                <RelativeTime timestamp={room.lastEventAt} />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
        </CardHeader>
        <CardContent>
          {events.length === 0 ? (
            <p className="text-sm text-elder-text-muted py-4 text-center">No recent events</p>
          ) : (
            <div className="space-y-2">
              {events.slice(0, 10).map(event => (
                <div key={event.id} className="flex items-center justify-between py-1.5 border-b border-elder-border last:border-0">
                  <div>
                    <p className="text-sm font-medium">
                      {event.eventType.replace('-', ' ')}
                      {event.bedZone && (
                        <span className="text-elder-text-muted ml-1">Bed {event.bedZone}</span>
                      )}
                    </p>
                    <RelativeTime timestamp={event.detectedAt} />
                  </div>
                  <Badge variant={event.status === 'resolved' ? 'success' : event.status === 'active' ? 'critical' : 'warning'}>
                    {event.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

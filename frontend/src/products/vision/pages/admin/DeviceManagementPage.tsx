import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { Card, CardContent, Spinner, Button, Modal, Input, Select, Toggle } from '@/components/ui';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { Badge } from '@/components/ui';
import { StatusDot } from '@/components/ui/StatusDot';
import { useDevices } from '../../hooks/useDevices';
import { useRoomsByUnit } from '../../hooks/useFacility';
import * as deviceService from '../../services/deviceService';
import type { Device, DeviceType } from '@/types';

// ── Device Modal ───────────────────────────────────────

function DeviceModal({
  isOpen,
  onClose,
  editingDevice,
  rooms,
}: {
  isOpen: boolean;
  onClose: (saved?: boolean) => void;
  editingDevice: Device | null;
  rooms: { id: string; number: string }[];
}) {
  const [name, setName] = useState(editingDevice?.name ?? '');
  const [roomId, setRoomId] = useState(editingDevice?.roomId ?? (rooms[0]?.id ?? ''));
  const [type, setType] = useState<DeviceType>(editingDevice?.type ?? 'ai-vision');
  const [edgeDeviceId, setEdgeDeviceId] = useState(editingDevice?.edgeDeviceId ?? '');
  const [enabled, setEnabled] = useState(editingDevice?.enabled ?? true);
  const [rtspUrl, setRtspUrl] = useState(editingDevice?.connectionConfig?.rtspUrl ?? '');
  const [serialPort, setSerialPort] = useState(editingDevice?.connectionConfig?.serialPort ?? '');
  const [baudRate, setBaudRate] = useState(String(editingDevice?.connectionConfig?.baudRate ?? '115200'));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const selectedRoom = rooms.find(r => r.id === roomId);

  async function handleSave() {
    if (!name.trim()) { setError('Device name is required'); return; }
    if (!roomId) { setError('Room is required'); return; }
    if (!edgeDeviceId.trim()) { setError('Edge Device ID is required'); return; }
    if (type === 'ai-vision' && !rtspUrl.trim()) { setError('RTSP URL is required for cameras'); return; }
    if (type === 'ai-sensor' && !serialPort.trim()) { setError('Serial port is required for sensors'); return; }

    const connectionConfig = type === 'ai-vision'
      ? { rtspUrl: rtspUrl.trim() }
      : { serialPort: serialPort.trim(), baudRate: Number(baudRate) };

    setSaving(true);
    if (editingDevice) {
      await deviceService.updateDevice(editingDevice.id, {
        name: name.trim(),
        roomId,
        roomNumber: selectedRoom?.number ?? '',
        type,
        edgeDeviceId: edgeDeviceId.trim(),
        enabled,
        connectionConfig,
      });
    } else {
      await deviceService.addDevice({
        name: name.trim(),
        roomId,
        roomNumber: selectedRoom?.number ?? '',
        type,
        edgeDeviceId: edgeDeviceId.trim(),
        enabled,
        connectionConfig,
      });
    }
    setSaving(false);
    onClose(true);
  }

  return (
    <Modal isOpen={isOpen} onClose={() => onClose()} title={editingDevice ? 'Edit Device' : 'Add Device'} size="sm">
      <div className="space-y-4">
        <Input label="Device Name" placeholder="e.g. Camera 101" value={name} onChange={e => { setName(e.target.value); setError(''); }} />
        <Select
          label="Room"
          value={roomId}
          onChange={e => { setRoomId(e.target.value); setError(''); }}
          options={rooms.map(r => ({ value: r.id, label: `Room ${r.number}` }))}
        />
        <Select
          label="Type"
          value={type}
          onChange={e => { setType(e.target.value as DeviceType); setError(''); }}
          options={[
            { value: 'ai-vision', label: 'AI Vision (Camera)' },
            { value: 'ai-sensor', label: 'AI Sensor (Radar)' },
          ]}
        />
        <Input label="Edge Device ID" placeholder="e.g. edge-floor1" value={edgeDeviceId} onChange={e => { setEdgeDeviceId(e.target.value); setError(''); }} />
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-elder-text-primary">Enabled</span>
          <Toggle checked={enabled} onChange={setEnabled} />
        </div>

        {/* Conditional connection fields */}
        {type === 'ai-vision' && (
          <Input label="RTSP URL" placeholder="rtsp://192.168.1.100:554/stream1" value={rtspUrl} onChange={e => { setRtspUrl(e.target.value); setError(''); }} />
        )}
        {type === 'ai-sensor' && (
          <>
            <Input label="Serial Port" placeholder="/dev/ttyUSB0" value={serialPort} onChange={e => { setSerialPort(e.target.value); setError(''); }} />
            <Input label="Baud Rate" type="number" placeholder="115200" value={baudRate} onChange={e => { setBaudRate(e.target.value); setError(''); }} />
          </>
        )}

        {error && <p className="text-sm text-elder-critical">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={() => onClose()}>Cancel</Button>
          <Button onClick={handleSave} loading={saving}>{editingDevice ? 'Save' : 'Add Device'}</Button>
        </div>
      </div>
    </Modal>
  );
}

// ── Delete Confirmation Modal ──────────────────────────

function DeleteModal({
  isOpen,
  onClose,
  onConfirm,
  label,
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  label: string;
}) {
  const [deleting, setDeleting] = useState(false);
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Confirm Delete" size="sm">
      <p className="text-sm text-elder-text-secondary mb-4">
        Are you sure you want to delete <strong>{label}</strong>? This action cannot be undone.
      </p>
      <div className="flex justify-end gap-2">
        <Button variant="secondary" onClick={onClose}>Cancel</Button>
        <Button
          variant="danger"
          loading={deleting}
          onClick={async () => {
            setDeleting(true);
            await onConfirm();
            setDeleting(false);
          }}
        >
          Delete
        </Button>
      </div>
    </Modal>
  );
}

// ── Status Display ─────────────────────────────────────

function DeviceStatusCell({ device }: { device: Device }) {
  if (!device.enabled) {
    return <Badge variant="default">Disabled</Badge>;
  }
  const colorMap = { online: 'green', degraded: 'yellow', offline: 'red' } as const;
  const labelMap = { online: 'Online', degraded: 'Degraded', offline: 'Offline' } as const;
  return (
    <span className="inline-flex items-center gap-1.5">
      <StatusDot color={colorMap[device.status]} />
      <span>{labelMap[device.status]}</span>
    </span>
  );
}

// ── Main Page ──────────────────────────────────────────

export function DeviceManagementPage() {
  const queryClient = useQueryClient();
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [roomFilter, setRoomFilter] = useState<string>('');

  const { data: devices, isLoading } = useDevices(
    typeFilter || roomFilter
      ? { type: typeFilter as DeviceType || undefined, roomId: roomFilter || undefined }
      : undefined
  );
  const { data: rooms } = useRoomsByUnit();

  const [deviceModal, setDeviceModal] = useState<{ open: boolean; editing: Device | null }>({ open: false, editing: null });
  const [deleteDevice, setDeleteDevice] = useState<Device | null>(null);

  function invalidateAll() {
    queryClient.invalidateQueries({ queryKey: ['devices'] });
  }

  const roomOptions = rooms?.map(r => ({ id: r.id, number: r.number })) ?? [];

  return (
    <div className="space-y-4">
      <PageHeader
        title="Device Management"
        subtitle="Manage cameras, sensors, and edge device connections"
      />

      <Card>
        <CardContent>
          <div className="flex items-center justify-between mb-4 gap-4">
            <div className="flex gap-3">
              <Select
                value={typeFilter}
                onChange={e => setTypeFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Types' },
                  { value: 'ai-vision', label: 'AI Vision' },
                  { value: 'ai-sensor', label: 'AI Sensor' },
                ]}
              />
              <Select
                value={roomFilter}
                onChange={e => setRoomFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Rooms' },
                  ...(rooms?.map(r => ({ value: r.id, label: `Room ${r.number}` })) ?? []),
                ]}
              />
            </div>
            <Button size="sm" onClick={() => setDeviceModal({ open: true, editing: null })}>
              <Plus className="h-4 w-4 mr-1" /> Add Device
            </Button>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-12"><Spinner /></div>
          ) : (
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Name</TableHead>
                  <TableHead>Room</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Edge Device</TableHead>
                  <TableHead>Latency</TableHead>
                  <TableHead>Uptime</TableHead>
                  <TableHead className="w-24">Actions</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {devices && devices.length > 0 ? (
                  devices.map(device => (
                    <TableRow key={device.id}>
                      <TableCell className="font-medium">{device.name || device.id}</TableCell>
                      <TableCell>{device.roomNumber ?? '—'}</TableCell>
                      <TableCell className="capitalize">
                        {device.type === 'ai-vision' ? 'Camera' : device.type === 'ai-sensor' ? 'Radar' : device.type}
                      </TableCell>
                      <TableCell><DeviceStatusCell device={device} /></TableCell>
                      <TableCell>
                        <span className="text-xs font-mono text-elder-text-muted">{device.edgeDeviceId ?? '—'}</span>
                      </TableCell>
                      <TableCell>
                        {device.status !== 'offline' ? `${device.inferenceLatencyMs}ms` : '—'}
                      </TableCell>
                      <TableCell>{device.uptime > 0 ? `${device.uptime.toFixed(1)}%` : '—'}</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <button
                            onClick={() => setDeviceModal({ open: true, editing: device })}
                            className="p-1.5 rounded hover:bg-gray-100 text-elder-text-muted hover:text-elder-action"
                            title="Edit"
                          >
                            <Pencil className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setDeleteDevice(device)}
                            className="p-1.5 rounded hover:bg-gray-100 text-elder-text-muted hover:text-elder-critical"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-sm text-elder-text-muted">
                      No devices found. Add a device to get started.
                    </td>
                  </tr>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* ── Modals ── */}
      {deviceModal.open && (
        <DeviceModal
          isOpen
          editingDevice={deviceModal.editing}
          rooms={roomOptions}
          onClose={(saved) => {
            setDeviceModal({ open: false, editing: null });
            if (saved) invalidateAll();
          }}
        />
      )}

      {deleteDevice && (
        <DeleteModal
          isOpen
          label={deleteDevice.name || deleteDevice.id}
          onClose={() => setDeleteDevice(null)}
          onConfirm={async () => {
            await deviceService.removeDevice(deleteDevice.id);
            setDeleteDevice(null);
            invalidateAll();
          }}
        />
      )}
    </div>
  );
}

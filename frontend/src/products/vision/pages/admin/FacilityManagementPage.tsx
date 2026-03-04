import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import { Card, CardContent, Tabs, TabPanel, Spinner, Button, Modal, Input, Select } from '@/components/ui';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui';
import { PageHeader } from '@/components/common/PageHeader';
import { Badge } from '@/components/ui';
import { useUnits, useRoomsByUnit } from '../../hooks/useFacility';
import * as facilityService from '@/services/facilityService';
import type { Unit, Room, RoomType, SensorType } from '@/types';

// ── Unit Modal ─────────────────────────────────────────

function UnitModal({
  isOpen,
  onClose,
  editingUnit,
}: {
  isOpen: boolean;
  onClose: (saved?: boolean) => void;
  editingUnit: (Unit & { roomCount: number }) | null;
}) {
  const [name, setName] = useState(editingUnit?.name ?? '');
  const [floor, setFloor] = useState(String(editingUnit?.floor ?? ''));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function handleSave() {
    if (!name.trim()) { setError('Unit name is required'); return; }
    if (!floor || isNaN(Number(floor))) { setError('Floor must be a number'); return; }
    setSaving(true);
    if (editingUnit) {
      await facilityService.updateUnit(editingUnit.id, name.trim(), Number(floor));
    } else {
      await facilityService.addUnit(name.trim(), Number(floor));
    }
    setSaving(false);
    onClose(true);
  }

  return (
    <Modal isOpen={isOpen} onClose={() => onClose()} title={editingUnit ? 'Edit Unit' : 'Add Unit'} size="sm">
      <div className="space-y-4">
        <Input label="Unit Name" placeholder="e.g. Unit C" value={name} onChange={e => { setName(e.target.value); setError(''); }} />
        <Input label="Floor" type="number" placeholder="e.g. 3" value={floor} onChange={e => { setFloor(e.target.value); setError(''); }} />
        {error && <p className="text-sm text-elder-critical">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={() => onClose()}>Cancel</Button>
          <Button onClick={handleSave} loading={saving}>{editingUnit ? 'Save' : 'Add Unit'}</Button>
        </div>
      </div>
    </Modal>
  );
}

// ── Room Modal ─────────────────────────────────────────

function RoomModal({
  isOpen,
  onClose,
  editingRoom,
  unitNames,
}: {
  isOpen: boolean;
  onClose: (saved?: boolean) => void;
  editingRoom: Room | null;
  unitNames: string[];
}) {
  const [roomNumber, setRoomNumber] = useState(editingRoom?.number ?? '');
  const [unit, setUnit] = useState(editingRoom?.unit ?? unitNames[0] ?? '');
  const [roomType, setRoomType] = useState<RoomType>(editingRoom?.roomType ?? 'single');
  const [sensorType, setSensorType] = useState<SensorType>(editingRoom?.sensorType ?? 'ai-vision');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function handleSave() {
    if (!roomNumber.trim()) { setError('Room number is required'); return; }
    if (!unit) { setError('Unit is required'); return; }
    setSaving(true);
    if (editingRoom) {
      await facilityService.updateRoom(editingRoom.id, {
        number: roomNumber.trim(),
        unit,
        roomType,
        sensorType,
      });
    } else {
      // Derive floor from selected unit's existing rooms or default to 1
      const units = await facilityService.getUnits();
      const selectedUnit = units.find(u => u.name === unit);
      const floor = selectedUnit?.floor ?? 1;
      await facilityService.addRoom(unit, floor, roomNumber.trim(), roomType, sensorType);
    }
    setSaving(false);
    onClose(true);
  }

  return (
    <Modal isOpen={isOpen} onClose={() => onClose()} title={editingRoom ? 'Edit Room' : 'Add Room'} size="sm">
      <div className="space-y-4">
        <Input label="Room Number" placeholder="e.g. 301" value={roomNumber} onChange={e => { setRoomNumber(e.target.value); setError(''); }} />
        <Select
          label="Unit"
          value={unit}
          onChange={e => { setUnit(e.target.value); setError(''); }}
          options={unitNames.map(n => ({ value: n, label: n }))}
        />
        <Select
          label="Room Type"
          value={roomType}
          onChange={e => setRoomType(e.target.value as RoomType)}
          options={[
            { value: 'single', label: 'Single' },
            { value: 'semi-private', label: 'Semi-Private' },
          ]}
        />
        <Select
          label="Sensor Type"
          value={sensorType}
          onChange={e => setSensorType(e.target.value as SensorType)}
          options={[
            { value: 'ai-vision', label: 'AI Vision' },
            { value: 'ai-sensor', label: 'AI Sensor' },
            { value: 'hybrid', label: 'Hybrid' },
          ]}
        />
        {error && <p className="text-sm text-elder-critical">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={() => onClose()}>Cancel</Button>
          <Button onClick={handleSave} loading={saving}>{editingRoom ? 'Save' : 'Add Room'}</Button>
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

// ── Main Page ──────────────────────────────────────────

export function FacilityManagementPage() {
  const queryClient = useQueryClient();
  const [tab, setTab] = useState('units');

  // Unit state
  const { data: units, isLoading: unitsLoading } = useUnits();
  const [unitModal, setUnitModal] = useState<{ open: boolean; editing: (Unit & { roomCount: number }) | null }>({ open: false, editing: null });
  const [deleteUnit, setDeleteUnit] = useState<(Unit & { roomCount: number }) | null>(null);

  // Room state
  const [roomUnitFilter, setRoomUnitFilter] = useState('');
  const { data: rooms, isLoading: roomsLoading } = useRoomsByUnit(roomUnitFilter || undefined);
  const [roomModal, setRoomModal] = useState<{ open: boolean; editing: Room | null }>({ open: false, editing: null });
  const [deleteRoom, setDeleteRoom] = useState<Room | null>(null);

  const unitNames = units?.map(u => u.name) ?? [];

  function invalidateAll() {
    queryClient.invalidateQueries({ queryKey: ['units'] });
    queryClient.invalidateQueries({ queryKey: ['unit-names'] });
    queryClient.invalidateQueries({ queryKey: ['facility-rooms'] });
    queryClient.invalidateQueries({ queryKey: ['rooms'] });
  }

  if (unitsLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-4">
      <PageHeader
        title="Facility Management"
        subtitle="Manage units, floors, and rooms"
      />

      <Tabs
        tabs={[
          { id: 'units', label: 'Units' },
          { id: 'rooms', label: 'Rooms' },
        ]}
        activeTab={tab}
        onChange={setTab}
      />

      {/* ── Units Tab ── */}
      <TabPanel id="units" activeTab={tab}>
        <Card>
          <CardContent>
            <div className="flex justify-end mb-4">
              <Button size="sm" onClick={() => setUnitModal({ open: true, editing: null })}>
                <Plus className="h-4 w-4 mr-1" /> Add Unit
              </Button>
            </div>
            <Table>
              <TableHeader>
                <tr>
                  <TableHead>Unit Name</TableHead>
                  <TableHead>Floor</TableHead>
                  <TableHead>Rooms</TableHead>
                  <TableHead className="w-24">Actions</TableHead>
                </tr>
              </TableHeader>
              <TableBody>
                {units && units.length > 0 ? (
                  units.map(unit => (
                    <TableRow key={unit.id}>
                      <TableCell className="font-medium">{unit.name}</TableCell>
                      <TableCell>{unit.floor}</TableCell>
                      <TableCell>
                        <Badge>{unit.roomCount}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <button
                            onClick={() => setUnitModal({ open: true, editing: unit })}
                            className="p-1.5 rounded hover:bg-gray-100 text-elder-text-muted hover:text-elder-action"
                            title="Edit"
                          >
                            <Pencil className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => setDeleteUnit(unit)}
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
                    <td colSpan={4} className="px-4 py-8 text-center text-sm text-elder-text-muted">
                      No units configured. Add a unit to get started.
                    </td>
                  </tr>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabPanel>

      {/* ── Rooms Tab ── */}
      <TabPanel id="rooms" activeTab={tab}>
        <Card>
          <CardContent>
            <div className="flex items-center justify-between mb-4 gap-4">
              <Select
                value={roomUnitFilter}
                onChange={e => setRoomUnitFilter(e.target.value)}
                options={[
                  { value: '', label: 'All Units' },
                  ...unitNames.map(n => ({ value: n, label: n })),
                ]}
              />
              <Button size="sm" onClick={() => setRoomModal({ open: true, editing: null })} disabled={unitNames.length === 0}>
                <Plus className="h-4 w-4 mr-1" /> Add Room
              </Button>
            </div>
            {roomsLoading ? (
              <div className="flex justify-center py-12"><Spinner /></div>
            ) : (
              <Table>
                <TableHeader>
                  <tr>
                    <TableHead>Room #</TableHead>
                    <TableHead>Unit</TableHead>
                    <TableHead>Floor</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Sensor</TableHead>
                    <TableHead>Residents</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-24">Actions</TableHead>
                  </tr>
                </TableHeader>
                <TableBody>
                  {rooms && rooms.length > 0 ? (
                    rooms.map(room => (
                      <TableRow key={room.id}>
                        <TableCell className="font-medium">{room.number}</TableCell>
                        <TableCell>{room.unit}</TableCell>
                        <TableCell>{room.floor}</TableCell>
                        <TableCell className="capitalize">{room.roomType}</TableCell>
                        <TableCell className="capitalize">{room.sensorType}</TableCell>
                        <TableCell>{room.residents.length}</TableCell>
                        <TableCell>
                          <span className={
                            room.status === 'clear' ? 'text-green-600' :
                            room.status === 'offline' ? 'text-gray-400' :
                            room.status === 'active-alert' ? 'text-red-600' :
                            'text-amber-500'
                          }>
                            {room.status === 'active-alert' ? 'Alert' : room.status.charAt(0).toUpperCase() + room.status.slice(1)}
                          </span>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <button
                              onClick={() => setRoomModal({ open: true, editing: room })}
                              className="p-1.5 rounded hover:bg-gray-100 text-elder-text-muted hover:text-elder-action"
                              title="Edit"
                            >
                              <Pencil className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => setDeleteRoom(room)}
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
                        No rooms found. Add a room to get started.
                      </td>
                    </tr>
                  )}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </TabPanel>

      {/* ── Modals ── */}
      {unitModal.open && (
        <UnitModal
          isOpen
          editingUnit={unitModal.editing}
          onClose={(saved) => {
            setUnitModal({ open: false, editing: null });
            if (saved) invalidateAll();
          }}
        />
      )}

      {roomModal.open && (
        <RoomModal
          isOpen
          editingRoom={roomModal.editing}
          unitNames={unitNames}
          onClose={(saved) => {
            setRoomModal({ open: false, editing: null });
            if (saved) invalidateAll();
          }}
        />
      )}

      {deleteUnit && (
        <DeleteModal
          isOpen
          label={`${deleteUnit.name} (${deleteUnit.roomCount} rooms)`}
          onClose={() => setDeleteUnit(null)}
          onConfirm={async () => {
            await facilityService.removeUnit(deleteUnit.id);
            setDeleteUnit(null);
            invalidateAll();
          }}
        />
      )}

      {deleteRoom && (
        <DeleteModal
          isOpen
          label={`Room ${deleteRoom.number}`}
          onClose={() => setDeleteRoom(null)}
          onConfirm={async () => {
            await facilityService.removeRoom(deleteRoom.id);
            setDeleteRoom(null);
            invalidateAll();
          }}
        />
      )}
    </div>
  );
}

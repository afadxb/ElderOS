from src.schemas.common import CamelModel


class UnitResponse(CamelModel):
    id: str
    name: str
    floor: int
    room_count: int


class CreateUnitRequest(CamelModel):
    name: str
    floor: int


class UpdateUnitRequest(CamelModel):
    name: str
    floor: int


class CreateRoomRequest(CamelModel):
    unit_name: str
    floor: int
    room_number: str
    room_type: str
    sensor_type: str


class UpdateRoomRequest(CamelModel):
    number: str | None = None
    room_type: str | None = None
    sensor_type: str | None = None
    unit: str | None = None
    floor: int | None = None

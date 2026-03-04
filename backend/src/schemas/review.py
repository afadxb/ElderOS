from typing import Literal

from src.schemas.common import CamelModel


class TriageRequest(CamelModel):
    action: Literal["confirm", "dismiss"]

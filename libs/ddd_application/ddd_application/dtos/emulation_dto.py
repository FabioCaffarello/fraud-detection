from dataclasses import dataclass

from domain.value_objects.emulation_id import EmulationID
from pydantic import BaseModel


@dataclass(frozen=True)
class EmulationScheduledDTO:
    """Data Transfer Object representing an emulation."""

    id: EmulationID
    emulator_sync: str
    emulation_domain: str
    timeout: int


class StartEmulatorDTO(BaseModel):
    """DTO for starting an emulation."""

    emulator_sync: str
    emulation_domain: str
    timeout: int

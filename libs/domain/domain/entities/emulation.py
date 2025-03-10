from datetime import datetime

from domain.value_objects.emulation_id import EmulationID


class Emulation:
    def __init__(self, timeout: int, emulator_type: str):
        self.id = EmulationID().generate()
        self.timeout = timeout
        self.emulator_type = emulator_type
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "timeout": self.timeout,
            "emulator_type": self.emulator_type,
            "created_at": self.created_at.isoformat(),
        }

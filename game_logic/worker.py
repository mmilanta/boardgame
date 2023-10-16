from typing import Optional

from .board import Coord
from .player import Player


class Worker:
    def __init__(
        self, location: Coord, id, owner: Player, name: Optional[str] = None
    ) -> None:
        self.location = location
        self.owner = owner
        self.id = id
        self.name = name if name else f"worker_{self.id}"
        self.yields = 1

    def yield_resources(self):
        return self.yields

    def to_dict(self):
        return {
            "location": self.location,
            "owner_id": self.owner.id,
            "id": self.id,
            "name": self.name,
        }

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

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Worker)
        if self.id != __value.id:
            return False
        assert self.location == __value.location
        assert self.owner == __value.owner
        assert self.name == __value.name
        assert self.yields == __value.yields
        return True

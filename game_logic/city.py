from board import Coord
from player import Player


class City:
    def __init__(self, location: Coord, id, owner: Player, name) -> None:
        self.location = location
        self.owner = owner
        self.id = id
        self.name = name if name else f"city_{self.id}"

    def serialize(self):
        return {
            "location": self.location,
            "owner_id": self.owner.id,
            "id": self.id,
            "name": self.name,
        }

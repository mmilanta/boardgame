import json

from .board import Coord
from .dice import DiceSet
from .player import Player


class Unit:
    def __init__(self, location: Coord, id, owner: Player, kind: str) -> None:
        self.location = location
        self.owner = owner
        self.id = id
        self.stats = UnitStats.from_kind(kind)
        self.actions = self.stats.movement

    def move_to(self, to: Coord) -> None:
        if self.location.distance(to) > self.actions:
            raise ValueError(f"Cannot move, only {self.actions} actions left")
        self.actions -= self.location.distance(to)
        self.location = to

    def serialize(self):
        return {
            "location": self.location,
            "owner_id": self.owner.id,
            "id": self.id,
            "kind": self.stats.kind,
        }

    def reset_upkeep(self):
        self.actions = self.stats.movement


class UnitStats:
    def __init__(
        self,
        kind: str,
        cost: int,
        attack_melee: DiceSet,
        attack_ranged: DiceSet,
        defense: DiceSet,
        movement: int,
        range: int,
    ) -> None:
        self.kind = kind
        self.cost = cost
        self.attack_melee = attack_melee
        self.attack_ranged = attack_ranged
        self.defense = defense
        self.movement = movement
        self.range = range

    @staticmethod
    def from_kind(kind: str):
        stats = json.load(open("game_logic/units_stats.json"))
        kwargs = {
            "kind": kind,
            "cost": stats[kind]["cost"],
            "attack_melee": DiceSet.from_dice_code(
                stats[kind]["attack_melee"]
            ),
            "attack_ranged": DiceSet.from_dice_code(
                stats[kind]["attack_ranged"]
            ),
            "defense": DiceSet.from_dice_code(stats[kind]["defense"]),
            "movement": stats[kind]["movement"],
            "range": stats[kind]["range"],
        }
        return UnitStats(**kwargs)

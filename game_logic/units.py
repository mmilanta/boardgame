import json
from typing import Dict

from .board import Coord
from .dice import DiceSet
from .player import Player


class Unit:
    def __init__(
        self, location: Coord, id: int, owner: Player, kind: str
    ) -> None:
        self.location: Coord = location
        self.owner: Player = owner
        self.id: int = id
        self.stats = UnitStats.from_kind(kind)
        self.actions = self.stats.movement

    def move_to(self, to: Coord) -> None:
        if self.location.distance(to) > self.actions:
            raise ValueError(f"Cannot move, only {self.actions} actions left")
        self.actions -= self.location.distance(to)
        self.location = to

    def to_dict(self):
        return {
            "location": self.location.to_dict(),
            "owner_id": self.owner.id,
            "id": self.id,
            "kind": self.stats.kind,
            "actions": self.actions,
        }

    @staticmethod
    def from_dict(Unit_dict: Dict) -> "Unit":
        new_unit = Unit(
            location=Coord.from_dict(Unit_dict["location"]),
            id=Unit_dict["id"],
            owner=Player(
                0, 0
            ),  # TODO: implement a smart way to link to the owner
            kind=Unit_dict["kind"],
        )
        new_unit.actions = Unit_dict["actions"]
        return new_unit

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

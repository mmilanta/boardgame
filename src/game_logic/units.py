import json
from enum import Enum

from pydantic import BaseModel

from src.game_logic.board import Board, Coord
from src.game_logic.dice import DiceSet


class UnitType(Enum):
    warrior = "warrior"
    archer = "archer"
    knight = "knight"
    defender = "defender"
    catapult = "catapult"


stats_dict = json.load(open("src/game_logic/units_stats.json"))


class UnitStats(BaseModel):
    type: UnitType
    cost: int
    attack_melee: DiceSet
    attack_ranged: DiceSet
    defense: DiceSet
    movement: int
    range: int

    @staticmethod
    def from_type(type: UnitType) -> "UnitStats":
        return UnitStats(
            type=type,
            cost=stats_dict[type.value]["cost"],
            attack_melee=DiceSet.from_dice_code(
                stats_dict[type.value]["attack_melee"]
            ),
            attack_ranged=DiceSet.from_dice_code(
                stats_dict[type.value]["attack_ranged"]
            ),
            defense=DiceSet.from_dice_code(stats_dict[type.value]["defense"]),
            movement=stats_dict[type.value]["movement"],
            range=stats_dict[type.value]["range"],
        )

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, UnitStats)
        if self.type != __value.type:
            return False
        assert self.cost == __value.cost
        assert self.attack_melee == __value.attack_melee
        assert self.attack_ranged == __value.attack_ranged
        assert self.defense == __value.defense
        assert self.movement == __value.movement
        assert self.range == __value.range
        return True


class Unit(BaseModel):
    location: Coord
    owner_id: int
    id: int
    type: UnitType
    actions: int

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Unit)
        if self.id != __value.id:
            return False
        assert self.location == __value.location
        assert self.owner_id == __value.owner_id
        assert self.stats == __value.stats
        assert self.actions == __value.actions
        return True

    def reset_upkeep(self):
        self.actions = self.stats.movement

    @property
    def stats(self) -> UnitStats:
        return UnitStats.from_type(self.type)


def move_unit(unit_to_move: Unit, to: Coord, board: Board) -> None:
    if board.distance(unit_to_move.location, to) > unit_to_move.actions:
        raise ValueError(
            f"Cannot move, only {unit_to_move.actions} actions left"
        )
    unit_to_move.actions -= unit_to_move.location.distance(to)
    unit_to_move.location = to

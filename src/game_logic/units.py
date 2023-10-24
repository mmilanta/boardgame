import json
from enum import Enum

from pydantic import BaseModel

from src.game_logic.board import Board, Coord
from src.game_logic.dice import DiceSet
from src.game_logic.exceptions import IllegalActionException


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

    def move_to(self, to: Coord, board: Board) -> None:
        if board.distance(self.location, to) > self.actions:
            raise IllegalActionException(
                f"Unit {self.id} cannot move: only {self.actions} actions left"
            )
        self.actions -= self.location.distance(to)
        self.location = to

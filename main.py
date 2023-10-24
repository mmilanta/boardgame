import logging
from enum import Enum
from typing import List

from pydantic import BaseModel

from src.game_logic.board import Coord
from src.game_logic.units import UnitType

logger = logging.getLogger(__name__)


class ActionType(Enum):
    move_unit = "move_unit"
    attack = "attack"
    build_unit = "build_unit"
    end_turn = "end_turn"


class ActionParam(BaseModel):
    action_type: ActionType
    game_id: int


class ActionParamMoveUnit(ActionParam):
    unit_id: int
    move_to: Coord


class ActionParamAttack(ActionParam):
    attacking_unit_ids: List[int]
    attacked_unit_id: int


class ActionParamBuildUnit(ActionParam):
    location: Coord
    type: UnitType


class ActionParamEndTurn(ActionParam):
    pass


class Action(BaseModel):
    action_type: ActionType
    game_id: int
    player_id: int
    params: ActionParam

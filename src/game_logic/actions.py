import json
import logging
import os
from enum import Enum
from typing import List, Union

from pydantic import BaseModel, ConfigDict, field_validator

from src.game_logic.board import HexCoord
from src.game_logic.exceptions import IllegalActionException
from src.game_logic.game import Game
from src.game_logic.units import Unit, UnitStats, UnitType

logger = logging.getLogger(__name__)


class ActionType(Enum):
    move_unit = "move_unit"
    attack = "attack"
    build_unit = "build_unit"
    end_turn = "end_turn"


class ActionParam(BaseModel):
    model_config = ConfigDict(extra="forbid")
    game_id: int
    player_id: int


class ActionParamMoveUnit(ActionParam):
    unit_id: int
    move_to: HexCoord


class ActionParamAttack(ActionParam):
    attacking_unit_ids: List[int]
    attacked_unit_id: int


class ActionParamBuildUnit(ActionParam):
    location: HexCoord
    type: UnitType


class ActionParamEndTurn(ActionParam):
    pass


class Action(BaseModel):
    action_type: ActionType
    params: Union[
        ActionParamMoveUnit,
        ActionParamAttack,
        ActionParamBuildUnit,
        ActionParamEndTurn,
    ]

    @field_validator("params", mode="after")
    def valid_params(cls, v, values):
        if values.data["action_type"] == ActionType.move_unit:
            assert isinstance(v, ActionParamMoveUnit)
        elif values.data["action_type"] == ActionType.attack:
            assert isinstance(v, ActionParamAttack)
        elif values.data["action_type"] == ActionType.build_unit:
            assert isinstance(v, ActionParamBuildUnit)
        elif values.data["action_type"] == ActionType.end_turn:
            assert isinstance(v, ActionParamEndTurn)
        return v


def action_move_unit(game: Game, params: ActionParamMoveUnit):
    if game.unit_from_location(params.move_to) is not None:
        raise IllegalActionException(
            f"Moving to occupied cell {params.move_to}"
        )

    unit = game.unit_from_id(params.unit_id)
    if unit.owner_id != params.player_id:
        raise IllegalActionException(
            f"Player {params.player_id} doesn't own the unit {params.unit_id}"
        )
    unit.move_to(to=params.move_to, board=game.board)


def action_attack(game: Game, params: ActionParamAttack):
    attacked_unit = game.unit_from_id(params.attacked_unit_id)
    if attacked_unit is None:
        raise IllegalActionException(
            f"Unit {params.attacked_unit_id} not found"
        )
    if attacked_unit.owner_id == params.player_id:
        raise IllegalActionException(
            f"""Player {params.player_id} cannot attach unit
            {attacked_unit.owner_id} as he is the owner"""
        )

    attacking_units: List[Unit] = []
    for attacking_unit_id in params.attacking_unit_ids:
        unit = game.unit_from_id(attacking_unit_id)
        if unit.owner_id != params.player_id:
            raise IllegalActionException(
                f"Player {params.player_id} doesn't own the unit {unit.id}"
            )
        attacking_units.append(unit)

    attacking_roll = 0
    for attacking_unit in attacking_units:
        if attacking_unit.location.distance(attacked_unit.location) == 0:
            raise AssertionError(
                """Incosistent status:
                attacking unit in the same cell as attacker"""
            )
        if attacking_unit.location.distance(attacked_unit.location) > 1:
            if attacking_unit.stats.attack_melee.is_zero:
                raise IllegalActionException(
                    f"Unit {attacking_unit} is melee, but attacking as ranged"
                )
            attacking_roll += attacking_unit.stats.attack_ranged.roll()
        if attacking_unit.location.distance(attacked_unit.location) == 1:
            if (
                attacked_unit.stats.attack_melee.expected()
                >= attacked_unit.stats.attack_ranged.expected()
            ):
                attacking_roll += attacking_unit.stats.attack_melee.roll()
            else:
                attacking_roll += attacking_unit.stats.attack_ranged.roll()
        if attacking_unit.actions == 0:
            raise IllegalActionException(
                f"Unit {attacking_unit} has no actions left"
            )

    attacked_roll = attacked_unit.stats.defense.roll()
    logger.info(
        f"""Units {params.attacking_unit_ids} attack {params.attacked_unit_id}.
        Total dice {attacking_roll} vs {attacked_roll}."""
    )

    for attacking_unit in attacking_units:
        attacking_unit.actions = 0

    if attacking_roll > attacked_roll:
        game.units.remove(attacked_unit)
        # pop unit from the list
        for attacking_unit in attacking_units:
            if (
                attacking_unit.location.distance(attacked_unit.location) == 1
                and attacked_unit.stats.attack_melee.expected()
                >= attacked_unit.stats.attack_ranged.expected()
            ):
                # needed to move
                attacking_unit.actions += 1
                attacking_unit.move_to(attacked_unit.location, game.board)


def action_build_unit(game: Game, params: ActionParamBuildUnit):
    if game.unit_from_location(params.location) is not None:
        raise IllegalActionException(
            f"Building unit in occupied cell {params.location}"
        )
    if (
        game.player_from_id(params.player_id).budget
        < UnitStats.from_type(params.type).cost
    ):
        raise IllegalActionException(
            f"""Player {params.player_id} doesnt have enough
            budget to build {params.type}"""
        )

    idx = 0
    for unit in game.units:
        idx = max(unit.id, idx) + 1

    new_unit = Unit(
        location=params.location,
        id=idx,
        owner_id=params.player_id,
        type=params.type,
        actions=0,
    )
    game.units.append(new_unit)


def action_end_turn(game: Game, params: ActionParamEndTurn):
    game.current_player_idx += 1
    if game.current_player_idx == len(game.players):
        game.current_player_idx = 0

    game.current_player.reset_upkeep()
    for unit in game.units:
        if unit.owner_id == game.current_player.id:
            unit.reset_upkeep()


def take_action(action: Action, file_dir: str = "data") -> Game:
    filename = os.path.join(file_dir, f"game_{action.params.game_id}.json")
    # check if files exists
    with open(filename, "r+") as f:
        game_dict = json.loads(f.read())
        game = Game(**game_dict)

        if game.current_player.id != action.params.player_id:
            raise IllegalActionException(
                f"Current player ({game.current_player.id}) is not the one "
                f"taking the action ({action.params.player_id})"
            )

        # action params
        if action.action_type == ActionType.move_unit:
            action_move_unit(game, action.params)
        elif action.action_type == ActionType.attack:
            action_attack(game, action.params)
        elif action.action_type == ActionType.build_unit:
            action_build_unit(game, action.params)
        elif action.action_type == ActionType.end_turn:
            action_end_turn(game, action.params)

        f.seek(0)
        f.write(json.dumps(game.model_dump(mode="json")))
        f.truncate()
    return game


def get_game(game_id: int) -> Game:
    filename = f"data/game_{game_id}.json"
    # check if files exists
    with open(filename, "r") as f:
        game_dict = json.loads(f.read())
        game = Game(**game_dict)
    return game


# TODO Create test for take action with temporary file.

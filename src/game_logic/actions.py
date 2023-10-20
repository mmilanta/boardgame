import json
import logging
from enum import Enum
from typing import List, Dict

from pydantic import BaseModel

from src.game_logic.board import Coord
from src.game_logic.game import Game
from src.game_logic.units import Unit, UnitType, move_unit

logger = logging.getLogger(__name__)


class ActionType(Enum):
    move_unit = "move_unit"
    attack = "attack"
    build_unit = "build_unit"
    end_turn = "end_turn"


class ActionParamMoveUnit(BaseModel):
    unit_id: int
    move_to: Coord


class ActionParamAttack(BaseModel):
    attacking_unit_ids: List[int]
    attacked_unit_id: int


class ActionParamBuildUnit(BaseModel):
    location: Coord
    type: UnitType


class ActionParamEndTurn(BaseModel):
    pass


class Action(BaseModel):
    action_type: ActionType
    game_id: int
    player_id: int
    params: Dict


def action_move_unit(game: Game, player_id: int, params: ActionParamMoveUnit):
    game.check_current_player(player_id)

    if game.unit_from_location(params.move_to) is not None:
        raise ValueError("Moving to used cell")

    unit = game.unit_from_id(params.unit_id)
    if unit.owner_id != player_id:
        raise ValueError("Player doesnt own the unit")
    move_unit(unit_to_move=unit, to=params.move_to, board=game.board)


def action_attack(game: Game, player_id: int, params: ActionParamAttack):
    game.check_current_player(player_id)

    attacked_unit = game.unit_from_id(params.attacked_unit_id)
    if attacked_unit is None:
        raise ValueError(f"Unit not found with id {params.attacked_unit_id}")
    if attacked_unit.owner_id == player_id:
        raise ValueError(
            f"""Cannot attach owned unit.
            Current player is {player_id}.
            Owner is {attacked_unit.owner_id}"""
        )

    attacking_units: List[Unit] = []
    for attacking_unit_id in params.attacking_unit_ids:
        unit = game.unit_from_id(attacking_unit_id)
        if unit.owner_id != player_id:
            raise ValueError("Player doesnt own the unit")
        attacking_units.append(unit)

    attacking_roll = 0
    for attacking_unit in attacking_units:
        if attacking_unit.location.distance(attacked_unit.location) == 0:
            raise ValueError(
                """Incosistent status:
                attacking unit in the same cell as attacker"""
            )
        if attacking_unit.location.distance(attacked_unit.location) > 1:
            if attacking_unit.stats.attack_melee.is_zero:
                raise ValueError("Melee unit used for ranged attack")
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
            raise ValueError("Attack no possible: no actions left")

    attacked_roll = attacked_unit.stats.defense.roll()
    logger.info(
        f"""Unit {params.attacking_unit_ids} attack {params.attacked_unit_id}.
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
                move_unit(attacking_unit, attacked_unit.location, game.board)
    return 1


def action_build_unit(
    game: Game, player_id: int, params: ActionParamBuildUnit
):
    game.check_current_player(player_id)
    if game.unit_from_location(params.location) is not None:
        raise ValueError("Unit already present in this cell")
    idx = 0
    for unit in game.units:
        idx = max(unit.id, idx) + 1
    new_unit = Unit(
        location=params.location,
        id=idx,
        owner_id=player_id,
        type=params.type,
        actions=0,
    )
    game.units.append(new_unit)


def action_end_turn(game: Game, player_id: int, params: ActionParamEndTurn):
    game.check_current_player(player_id)
    game.current_player_idx += 1
    if game.current_player_idx == len(game.players):
        game.current_player_idx = 0

    game.current_player.reset_upkeep()
    for unit in game.units:
        if unit.owner_id == game.current_player.id:
            unit.reset_upkeep()


def take_action(action: Action) -> Game:
    filename = f"data/game_{action.game_id}.json"
    # check if files exists
    with open(filename, "r+") as f:
        game_dict = json.loads(f.read())
        game = Game(**game_dict)

        # action params
        if action.action_type == ActionType.move_unit:
            action_move_unit(game, action.player_id, ActionParamMoveUnit(**action.params))
        elif action.action_type == ActionType.attack:
            action_attack(game, action.player_id, ActionParamAttack(**action.params))
        elif action.action_type == ActionType.build_unit:
            action_build_unit(game, action.player_id, ActionParamBuildUnit(**action.params))
        elif action.action_type == ActionType.end_turn:
            action_end_turn(game, action.player_id, ActionParamEndTurn(**action.params))

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

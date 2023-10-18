from src.game_logic.player import Player
from src.game_logic.game import Game
from src.game_logic.board import Coord
from src.game_logic.units import Unit, move_unit
from typing import List
import logging

logger = logging.getLogger(__name__)


class Action:
    @staticmethod
    def action_move_unit(game: Game, player: Player, unit_id: int, move_to: Coord):
        game.check_current_player(player)

        if game.unit_from_location(move_to) is not None:
            raise ValueError("Moving to used cell")

        unit = game.select_unit_from_id_and_player(unit_id, player)
        move_unit(unit_to_move=unit, to=move_to, board=game.board)

    @staticmethod
    def action_attack(
        game,
        player: Player,
        attacking_unit_ids: List[int],
        attacked_unit_id: int,
    ):
        game._check_current_player(player)

        attacked_unit = game._unit_from_id(attacked_unit_id)
        if attacked_unit is None:
            raise ValueError(f"Unit not found with id {attacked_unit_id}")
        if attacked_unit.owner == player:
            raise ValueError(
                f"""Cannot attach owned unit.
                Current player is {player.id}.
                Owner is {attacked_unit.owner.id}"""
            )

        attacking_units = []
        for attacking_unit_id in attacking_unit_ids:
            attacking_units.append(
                game._select_unit_from_id_and_player(attacking_unit_id, player)
            )

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
            f"""Unit {attacking_unit_ids} attack {attacked_unit_id}.
            Total dice {attacking_roll} vs {attacked_roll}."""
        )

        for attacking_unit in attacking_units:
            attacking_unit.actions = 0

        if attacking_roll > attacked_roll:
            game.units.remove(attacked_unit)
            # pop unit from the list
            for attacking_unit in attacking_units:
                if (
                    attacking_unit.location.distance(attacked_unit.location)
                    == 1
                    and attacked_unit.stats.attack_melee.expected()
                    >= attacked_unit.stats.attack_ranged.expected()
                ):
                    # needed to move
                    attacking_unit.actions += 1
                    attacking_unit.move_to(attacked_unit.location)
        return 1

    @staticmethod
    def action_build_unit(game, player: Player, location: Coord, kind: str):
        game._check_current_player(player)
        if game._unit_from_location(location) is not None:
            raise ValueError("Unit already present in this cell")
        idx = 0
        for unit in game.units:
            idx = max(unit.id, idx) + 1
        new_unit = Unit(location=location, id=idx, owner=player, kind=kind)
        game.units.append(new_unit)

    @staticmethod
    def action_end_turn(game: Game, player: Player):
        game.check_current_player(player)
        game.current_player_idx += 1
        if game.current_player_idx == len(game.players):
            game.current_player_idx = 0

        game.current_player.reset_upkeep()
        for unit in game.units:
            if unit.owner_id == game.current_player.id:
                unit.reset_upkeep()

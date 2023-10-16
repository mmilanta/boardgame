import logging
from copy import deepcopy
from typing import List

from .board import Board, Coord
from .player import Player
from .units import Unit
from .worker import Worker

logger = logging.getLogger()


class Game:
    def __init__(self, board: Board, players: List[Player]) -> None:
        self.board: Board = board
        self.players: List[Player] = players
        self.units: List[Unit] = []
        self.workers: List[Worker] = []
        self.current_player_idx: int = 0

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    def _check_current_player(self, player: Player):
        if player != self.current_player:
            raise ValueError("Wrong player is moving")

    def _unit_from_location(self, location: Coord):
        for unit in self.units:
            if unit.location == location:
                return unit
        return None

    def _unit_from_id(self, unit_id: int):
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        return None

    def _select_unit_from_id_and_player(self, unit_id: int, player: Player):
        unit = self._unit_from_id(unit_id)
        if unit is None:
            raise ValueError(f"Unit not found with id {unit_id}")
        if player != unit.owner:
            raise ValueError(
                f"""Unit not owned. Current player is {player.id}.
                Owner is {unit.owner.id}"""
            )
        return unit

    def _worker_from_location(self, location: Coord):
        for worker in self.workers:
            if worker.location == location:
                return worker
        return None

    # Actions:
    def action_move_unit(self, player: Player, unit_id: int, move_to: Coord):
        self._check_current_player(player)

        if self._unit_from_location(move_to) is not None:
            raise ValueError("Moving to used cell")

        unit = self._select_unit_from_id_and_player(unit_id, player)
        unit.move_to(move_to)
        return 1

    def action_attack(
        self,
        player: Player,
        attacking_unit_ids: List[int],
        attacked_unit_id: int,
    ):
        self._check_current_player(player)

        attacked_unit = self._unit_from_id(attacked_unit_id)
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
                self._select_unit_from_id_and_player(attacking_unit_id, player)
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
            self.units.remove(attacked_unit)
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

    def action_build_unit(self, player: Player, location: Coord, kind: str):
        self._check_current_player(player)
        if self._unit_from_location(location) is not None:
            raise ValueError("Unit already present in this cell")
        idx = 0
        for unit in self.units:
            idx = max(unit.id, idx) + 1
        new_unit = Unit(location=location, id=idx, owner=player, kind=kind)
        self.units.append(new_unit)

    def action_place_worker(self, player: Player, location: Coord):
        if not player.worker_to_place:
            raise ValueError(f"Worker already placed by player {player.id}")
        if self._worker_from_location(location) is not None:
            raise ValueError(f"Worker already present in {location}")
        player.worker_to_place = False
        idx = 0
        for worker in self.workers:
            idx = max(worker.id, idx) + 1
        new_worker = Worker(location, idx, player)
        self.workers.append(new_worker)

    def action_end_turn(self, player: Player):
        self._check_current_player(player)
        self.current_player_idx += 1
        if self.current_player_idx == len(self.players):
            self.current_player_idx = 0

        self.current_player.reset_upkeep()
        for unit in self.units:
            if unit.owner == self.current_player:
                unit.reset_upkeep()

        for worker in self.workers:
            if worker.owner == self.current_player:
                self.current_player.budget += worker.yield_resources()

    def to_dict(self):
        return {
            "board": self.board.to_dict(),
            "players": [player.to_dict() for player in self.players],
            "current_player_id": self.current_player.id,
            "units": [unit.to_dict() for unit in self.units],
        }

    @staticmethod
    def from_dict(dict_Game):
        players = [
            Player.from_dict(dict_Player)
            for dict_Player in dict_Game["players"]
        ]
        new_game = Game(
            board=Board.from_dict(dict_Game["board"]), players=players
        )
        current_player_idxs = [
            i
            for i, player in enumerate(players)
            if player.id == dict_Game["current_player_id"]
        ]
        assert len(current_player_idxs) == 1
        new_game.current_player_idx = current_player_idxs[0]

        def get_player_from_id(id: int):
            for p in players:
                if p.id == id:
                    return p
            raise ValueError("This id does not belong to any player")

        new_game.units = [
            Unit.from_dict(
                dict_Unit, get_player_from_id(dict_Unit["owner_id"])
            )
            for dict_Unit in dict_Game["units"]
        ]
        return new_game

    def render(self):
        for player in self.players:
            print(f"{player.id}: {player.budget}$")
        print("---" * self.board.width)
        output = deepcopy(self.board.raw_board)
        for row in range(self.board.height):
            for col in range(self.board.width):
                output[row][col] = "  "
        for unit in self.units:
            output[unit.location.row][unit.location.col] = (
                unit.stats.kind[0] + str(unit.owner.id)[0]
            )
        return "\n".join(["|".join(row) for row in output])

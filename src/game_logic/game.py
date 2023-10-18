import logging
from copy import deepcopy
from typing import List

from pydantic import BaseModel

from src.game_logic.board import Board, Coord
from src.game_logic.player import Player
from src.game_logic.units import Unit

logger = logging.getLogger()


class Game(BaseModel):
    board: Board
    players: List[Player]
    units: List[Unit]
    current_player_idx: int

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Game)
        return (
            self.board == __value.board
            and self.players == __value.players
            and self.units == __value.units
            and self.workers == __value.workers
            and self.current_player_idx == __value.current_player_idx
        )

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    def check_current_player(self, player_id: int):
        if player_id != self.current_player.id:
            raise ValueError("Wrong player is moving")

    def unit_from_location(self, location: Coord):
        for unit in self.units:
            if unit.location == location:
                return unit
        return None

    def unit_from_id(self, unit_id: int):
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        return None

    def select_unit_from_id_and_player(self, unit_id: int, player: Player):
        unit = self._unit_from_id(unit_id)
        if unit is None:
            raise ValueError(f"Unit not found with id {unit_id}")
        if player != unit.owner:
            raise ValueError(
                f"""Unit not owned. Current player is {player.id}.
                Owner is {unit.owner.id}"""
            )
        return unit

    def build_empty(board: Board, players: List[Player]) -> "Game":
        return Game(
            board=board, players=players, units=[], current_player_idx=0
        )


def render_game(game: Game):
    for player in game.players:
        print(f"{player.id}: {player.budget}$")
    print("---" * game.board.width)
    output = deepcopy(game.board.raw_board)
    for row in range(game.board.height):
        for col in range(game.board.width):
            output[row][col] = "  "
    for unit in game.units:
        output[unit.location.row][unit.location.col] = (
            unit.stats.kind[0] + str(unit.owner.id)[0]
        )
    return "\n".join(["|".join(row) for row in output])

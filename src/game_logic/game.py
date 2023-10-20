import logging
from typing import List, Optional

from pydantic import BaseModel, ValidationError, field_validator

from src.game_logic.board import Board, Coord
from src.game_logic.player import Player
from src.game_logic.units import Unit

logger = logging.getLogger()


class Game(BaseModel):
    board: Board
    players: List[Player]
    units: List[Unit]
    current_player_idx: int

    @field_validator("players")
    def players_unique_id(cls, v):
        player_ids = [p.id for p in v]
        if len(player_ids) > len(set(player_ids)):
            raise ValidationError("Player ids must be unique")
        return v

    @field_validator("units")
    def units_unique_id(cls, v):
        units_ids = [u.id for u in v]
        if len(units_ids) > len(set(units_ids)):
            raise ValidationError("Unit ids must be unique")
        return v

    @field_validator("units")
    def units_owner_id_exists(cls, v, values):
        players_ids = [p.id for p in values.data["players"]]
        for unit in v:
            if unit.owner_id not in players_ids:
                raise ValidationError(
                    "Unit owner id must correspond to existing player"
                )
        return v

    @field_validator("units")
    def units_are_in_valid_locations(cls, v, values):
        [values.data["board"].valid_coord(unit.location) for unit in v]
        return v

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Game)
        return (
            self.board == __value.board
            and self.players == __value.players
            and self.units == __value.units
            and self.current_player_idx == __value.current_player_idx
        )

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    def check_current_player(self, player_id: int):
        if player_id != self.current_player.id:
            raise ValueError("Wrong player is moving")

    def unit_from_location(self, location: Coord) -> Optional[Unit]:
        for unit in self.units:
            if unit.location == location:
                return unit
        return None

    def unit_from_id(self, unit_id: int):
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        return None

    def player_from_id(self, player_id: int):
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def build_empty(board: Board, players: List[Player]) -> "Game":
        return Game(
            board=board, players=players, units=[], current_player_idx=0
        )


def render_game(game: Game):
    for player in game.players:
        print(f"{player.id}: {player.budget}$")
    print("---" * game.board.width)
    output = [["  "] * game.board.height for _ in game.board.width]
    for unit in game.units:
        output[unit.location.row][unit.location.col] = (
            unit.stats.kind[0] + str(unit.owner.id)[0]
        )
    return "\n".join(["|".join(row) for row in output])

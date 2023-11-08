import json
import logging
from os import listdir
from typing import List, Optional

from pydantic import BaseModel, ValidationError, field_validator

from src.game_logic.board import HexBoard, HexCoord
from src.game_logic.player import Player
from src.game_logic.units import Unit

logger = logging.getLogger()


class Game(BaseModel):
    board: HexBoard
    players: List[Player]
    units: List[Unit]
    current_player_idx: int

    @field_validator("players")
    def players_unique_id(cls, v):
        player_ids = [p.id for p in v]
        if len(player_ids) > len(set(player_ids)):
            raise ValidationError(
                "Game model corrupted: Player ids must be unique"
            )
        return v

    @field_validator("units")
    def units_unique_id(cls, v):
        units_ids = [u.id for u in v]
        if len(units_ids) > len(set(units_ids)):
            raise ValidationError(
                "Game model corrupted: Unit ids must be unique"
            )
        return v

    @field_validator("units")
    def units_owner_id_exists(cls, v, values):
        players_ids = [p.id for p in values.data["players"]]
        for unit in v:
            if unit.owner_id not in players_ids:
                raise ValidationError(
                    """Game model corrupted:
                    Unit owner id must correspond to existing player"""
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

    def unit_from_location(self, location: HexCoord) -> Optional[Unit]:
        for unit in self.units:
            if unit.location == location:
                return unit
        return None

    def unit_from_id(self, unit_id: int) -> Unit:
        for unit in self.units:
            if unit.id == unit_id:
                return unit
        raise ValueError(f"Unit {unit_id} not found")
        return None

    def player_from_id(self, player_id: int) -> Player:
        for player in self.players:
            if player.id == player_id:
                return player
        raise ValueError(f"Player {player_id} not found")

    def build_empty(board: HexBoard, players: List[Player]) -> "Game":
        return Game(
            board=board, players=players, units=[], current_player_idx=0
        )


def get_game(game_id: int) -> Game:
    filename = f"data/games/{game_id:03}.json"
    # check if files exists
    with open(filename, "r") as f:
        game_dict = json.loads(f.read())
        game = Game(**game_dict)
    return game


def new_game(game: Game, game_id: int | None) -> int:
    if game_id is None:
        game_id = 0
        for file_path in listdir("data/games"):
            game_id = max(int(file_path[:-5]) + 1, game_id)
    filename = f"data/games/{game_id:03}.json"
    with open(filename, "w") as f:
        f.write(json.dumps(game.model_dump(mode="json")))
    return game_id

from typing import Tuple

from src.game_logic.board import Board, Coord
from src.game_logic.player import Player
from src.game_logic.units import Unit, UnitType
from src.game_logic.game import Game
from src.game_logic.dice import DiceSet
import json
import pytest


@pytest.mark.parametrize("size", [
    (2, 2), (5, 5), (10, 5)
])
def test_board(size: Tuple[int, int]):
    board = Board.build_empty(*size)
    board2 = Board(**json.loads(json.dumps(board.model_dump(mode="json"))))
    assert board == board2


@pytest.mark.parametrize("coords", [
    (2, 3), (15, 5), (10, 5)
])
def test_coord(coords: Tuple[int, int]):
    coord = Coord(row=coords[0], col=coords[1])
    coord2 = Coord(**json.loads(json.dumps(coord.model_dump(mode="json"))))
    assert coord == coord2


@pytest.mark.parametrize("id, budget, worker_to_place", [
    (0, 10, True), (2, 3, False), (1, 0, True)
])
def test_player(id, budget, worker_to_place):
    player = Player(id=id, budget=budget, worker_to_place=worker_to_place)
    player2 = Player(**json.loads(json.dumps(player.model_dump(mode="json"))))
    assert player == player2


@pytest.mark.parametrize("location, owner_id, id, type", [
    (Coord(row=2, col=3), 10, 0, UnitType.archer),
    (Coord(row=3, col=4), 9, 1, UnitType.warrior),
    (Coord(row=2, col=3), 8, 2, UnitType.catapult),
    (Coord(row=3, col=4), 7, 3, UnitType.defender),
    (Coord(row=2, col=3), 6, 4, UnitType.knight),
])
def test_unit(location, owner_id, id, type):
    unit = Unit(location=location,
                owner_id=owner_id,
                id=id,
                type=type,
                actions=0)
    unit2 = Unit(**json.loads(json.dumps(unit.model_dump(mode="json"))))
    assert unit == unit2


@pytest.mark.parametrize("board, players, units, current_player_idx", [
    (Board.build_empty(10, 10), [
        Player(id=0, budget=10, worker_to_place=False),
        Player(id=1, budget=10, worker_to_place=False)
    ], [
        Unit(location=Coord(row=0, col=1),
             id=0,
             owner_id=0,
             type=UnitType.warrior,
             actions=0),
        Unit(location=Coord(row=0, col=1),
             id=1,
             owner_id=1,
             type=UnitType.archer,
             actions=0),
    ], 0)
])
def test_game(board, players, units, current_player_idx):
    game = Game(board=board,
                players=players,
                units=units,
                current_player_idx=current_player_idx)
    game2 = Game(**json.loads(json.dumps(game.model_dump(mode="json"))))
    assert game == game2


@pytest.mark.parametrize("diceset_str", [
    "4d10", "5d5", "1d2", "3d3"
])
def test_diceset(diceset_str):
    diceset = DiceSet.from_dice_code(diceset_str)
    expected = diceset.expected()
    N = 10_000
    mean_roll = 0
    for _ in range(N):
        mean_roll += diceset.roll()
    mean_roll /= N
    assert abs(mean_roll - expected) < .1

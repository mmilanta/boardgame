import json
from typing import Tuple

import pytest

from src.game_logic.board import HexBoard, HexCoord
from src.game_logic.city import City
from src.game_logic.dice import DiceSet
from src.game_logic.game import Game
from src.game_logic.player import Player
from src.game_logic.units import Unit, UnitType, Worker


@pytest.mark.parametrize("radius", [5, 10, 23])
def test_board(radius: int):
    board = HexBoard.build_circular(radius=radius)
    board2 = HexBoard(**json.loads(json.dumps(board.model_dump(mode="json"))))
    print(board2)
    assert board == board2


@pytest.mark.parametrize("coords", [(2, 3, -5), (15, 5, -20), (10, 5, -15)])
def test_coord(coords: Tuple[int, int, int]):
    coord = HexCoord(q=coords[0], r=coords[1], s=coords[2])
    coord2 = HexCoord(**json.loads(json.dumps(coord.model_dump(mode="json"))))
    assert coord == coord2


@pytest.mark.parametrize(
    "id, budget, worker_to_place", [(0, 10, True), (2, 3, False), (1, 0, True)]
)
def test_player(id, budget, worker_to_place):
    player = Player(id=id, budget=budget, worker_to_place=worker_to_place)
    player2 = Player(**json.loads(json.dumps(player.model_dump(mode="json"))))
    assert player == player2


@pytest.mark.parametrize(
    "location, owner_id, id, type",
    [
        (HexCoord(q=2, r=3, s=-5), 10, 0, UnitType.archer),
        (HexCoord(q=3, r=4, s=-7), 9, 1, UnitType.warrior),
        (HexCoord(q=2, r=3, s=-5), 8, 2, UnitType.catapult),
        (HexCoord(q=3, r=4, s=-7), 7, 3, UnitType.defender),
        (HexCoord(q=2, r=3, s=-5), 6, 4, UnitType.knight),
    ],
)
def test_unit(location, owner_id, id, type):
    unit = Unit(
        location=location, owner_id=owner_id, id=id, type=type, actions=0
    )
    unit2 = Unit(**json.loads(json.dumps(unit.model_dump(mode="json"))))
    assert unit == unit2


@pytest.mark.parametrize(
    "board, players, units, cities, current_player_idx",
    [
        (
            HexBoard.build_circular(10),
            [
                Player(id=0, budget=10, worker_to_place=False),
                Player(id=1, budget=10, worker_to_place=False),
            ],
            [
                Unit(
                    location=HexCoord(q=0, r=1, s=-1),
                    id=0,
                    owner_id=0,
                    type=UnitType.warrior,
                    actions=0,
                ),
                Unit(
                    location=HexCoord(q=1, r=1, s=-2),
                    id=1,
                    owner_id=1,
                    type=UnitType.archer,
                    actions=0,
                ),
            ],
            [
                City(
                    location=HexCoord(q=1, r=1, s=-2),
                    id=0,
                    owner_id=0,
                    name="london",
                    workers=[
                        Worker(
                            location=HexCoord(q=1, r=2, s=-3), id=0, yields=1
                        )
                    ],
                )
            ],
            0,
        )
    ],
)
def test_game(board, players, units, cities, current_player_idx):
    game = Game(
        board=board,
        players=players,
        units=units,
        cities=cities,
        current_player_idx=current_player_idx,
    )
    game2 = Game(**json.loads(json.dumps(game.model_dump(mode="json"))))
    assert game == game2


@pytest.mark.parametrize("diceset_str", ["4d10", "5d5", "1d2", "3d3"])
def test_diceset(diceset_str):
    diceset = DiceSet.from_dice_code(diceset_str)
    expected = diceset.expected()
    N = 100_000
    mean_roll = 0
    for _ in range(N):
        mean_roll += diceset.roll()
    mean_roll /= N
    assert abs(mean_roll - expected) < 0.1

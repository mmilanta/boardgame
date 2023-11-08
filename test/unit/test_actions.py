import json
import os
import tempfile
from typing import Dict

import pytest
from pydantic import ValidationError

from src.game_logic.actions import Action, take_action
from src.game_logic.board import HexBoard, HexCoord
from src.game_logic.exceptions import IllegalActionException
from src.game_logic.game import Game
from src.game_logic.player import Player
from src.game_logic.units import Unit, UnitType

action_list = [
    pytest.param(
        {
            "action_type": "move_unit",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "unit_id": 2,
                "move_to": {
                    "q": 2,
                    "r": 0,
                    "s": -2,
                },
            },
        },
        True,
        id="move_unit",
    ),
    pytest.param(
        {
            "action_type": "attack",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "attacking_unit_ids": [2],
                "attacked_unit_id": 3,
            },
        },
        True,
        id="attack",
    ),
    pytest.param(
        {
            "action_type": "build_unit",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "location": {
                    "q": 3,
                    "r": 3,
                    "s": -6,
                },
                "type": "warrior",
            },
        },
        True,
        id="build_unit",
    ),
    pytest.param(
        {
            "action_type": "end_turn",
            "params": {"game_id": 0, "player_id": 0},
        },
        True,
        id="end_turn",
    ),
    pytest.param(
        {
            "action_type": "attack",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "unit_id": 0,
                "move_to": {
                    "q": 0,
                    "r": 0,
                    "s": 0,
                },
            },
        },
        False,
        id="attack_fail",
    ),
    pytest.param(
        {
            "action_type": "build_unit",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "attacking_unit_ids": [0, 1, 2],
                "attacked_unit_id": 3,
            },
        },
        False,
        id="build_unit_fail",
    ),
    pytest.param(
        {
            "action_type": "attack",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "location": {
                    "q": 0,
                    "r": 0,
                    "s": 0,
                },
                "type": "warrior",
            },
        },
        False,
        id="attack_fail",
    ),
    pytest.param(
        {
            "action_type": "end_turn",
            "params": {
                "game_id": 0,
                "player_id": 0,
                "location": {
                    "q": 0,
                    "r": 0,
                    "s": 0,
                },
                "type": "warrior",
            },
        },
        False,
        id="end_turn_fail",
    ),
]


@pytest.fixture
def temporary_directory_with_game():
    game = Game(
        board=HexBoard.build_circular(10),
        players=[Player(id=idx, budget=10) for idx in range(4)],
        units=[
            Unit(
                location=HexCoord(q=0, r=0, s=0),
                owner_id=0,
                id=0,
                type=UnitType.warrior,
                actions=1,
            ),
            Unit(
                location=HexCoord(q=1, r=-1, s=0),
                owner_id=0,
                id=1,
                type=UnitType.archer,
                actions=0,
            ),
            Unit(
                location=HexCoord(q=1, r=0, s=-1),
                owner_id=0,
                id=2,
                type=UnitType.catapult,
                actions=1,
            ),
            Unit(
                location=HexCoord(q=0, r=1, s=-1),
                owner_id=1,
                id=3,
                type=UnitType.warrior,
                actions=0,
            ),
        ],
        current_player_idx=0,
    )
    with tempfile.TemporaryDirectory() as tempdir:
        os.makedirs(os.path.join(tempdir, "games"))
        json.dump(
            game.model_dump(mode="json"),
            open(os.path.join(tempdir, "games/000.json"), "w"),
        )
        yield tempdir


@pytest.mark.parametrize(
    "serialized_action, valid",
    action_list,
)
def test_action_request_validation(
    serialized_action: Dict, valid: bool, temporary_directory_with_game
):
    try:
        action = Action(**serialized_action)
        assert valid
        take_action(
            action,
            file_dir=os.path.join(temporary_directory_with_game, "games"),
        )
    except (ValidationError, IllegalActionException) as e:
        print(e)
        assert not valid

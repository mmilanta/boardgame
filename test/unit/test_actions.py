from typing import Dict

import pytest
from pydantic import ValidationError

from src.game_logic.actions import Action


@pytest.mark.parametrize(
    "serialized_action, valid",
    [
        (
            {
                "action_type": "move_unit",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "unit_id": 0,
                    "move_to": {
                        "row": 0,
                        "col": 0,
                    },
                },
            },
            True,
        ),
        (
            {
                "action_type": "attack",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "attacking_unit_ids": [0, 1, 2],
                    "attacked_unit_id": 3,
                },
            },
            True,
        ),
        (
            {
                "action_type": "build_unit",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "location": {
                        "row": 0,
                        "col": 0,
                    },
                    "type": "warrior",
                },
            },
            True,
        ),
        (
            {
                "action_type": "end_turn",
                "params": {"game_id": 0, "player_id": 1},
            },
            True,
        ),
        (
            {
                "action_type": "attack",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "unit_id": 0,
                    "move_to": {
                        "row": 0,
                        "col": 0,
                    },
                },
            },
            False,
        ),
        (
            {
                "action_type": "build_unit",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "attacking_unit_ids": [0, 1, 2],
                    "attacked_unit_id": 3,
                },
            },
            False,
        ),
        (
            {
                "action_type": "attack",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "location": {
                        "row": 0,
                        "col": 0,
                    },
                    "type": "warrior",
                },
            },
            False,
        ),
        (
            {
                "action_type": "end_turn",
                "params": {
                    "game_id": 0,
                    "player_id": 1,
                    "location": {
                        "row": 0,
                        "col": 0,
                    },
                    "type": "warrior",
                },
            },
            False,
        ),
    ],
)
def test_action_request_validation(serialized_action: Dict, valid: bool):
    try:
        _ = Action(**serialized_action)
        assert valid
    except ValidationError:
        assert not valid

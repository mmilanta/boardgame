from typing import Optional, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.game_logic.actions import Action, take_action
from src.game_logic.board import HexBoard
from src.game_logic.exceptions import IllegalActionException
from src.game_logic.game import Game, get_game, new_game
from src.game_logic.player import Player

app = FastAPI()


@app.get("/game")
def get_game_endpoint(game_id: int) -> Game:
    return get_game(game_id)


@app.post("/action")
def post_action_endpoint(action: Action) -> Game:
    game = take_action(action=action)
    return game


@app.post("/new_game")
def new_game_endpoint(
    game_id: Optional[int], radius: int, n_players: int
) -> Tuple[Game, int]:
    board = HexBoard.build_circular(radius=radius)
    game = Game.build_empty(
        board=board,
        players=[Player(id=i, budget=10) for i in range(n_players)],
    )
    game_id = new_game(game=game, game_id=game_id)
    return game, game_id


@app.exception_handler(IllegalActionException)
def unsupported_language_exception_handler(
    request: Request, exc: IllegalActionException
):
    return JSONResponse(
        status_code=400,
        content={"message": f"IllegalActionException: {str(exc)}"},
    )

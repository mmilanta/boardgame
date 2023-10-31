from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


from src.game_logic.actions import Action, get_game, take_action
from src.game_logic.board import Board
from src.game_logic.game import Game
from src.game_logic.player import Player
from src.game_logic.exceptions import IllegalActionException

app = FastAPI()

board = Board.build_empty(10, 10)
players = [Player(id=i, budget=10) for i in range(2)]
game = Game.build_empty(board=board, players=players)


@app.get("/game")
def get_game_endpoint(game_id: int) -> Game:
    return get_game(game_id)


@app.post("/action")
def post_action_endpoint(action: Action) -> Game:
    game = take_action(action=action)
    return game


@app.exception_handler(IllegalActionException)
def unsupported_language_exception_handler(
    request: Request, exc: IllegalActionException
):
    return JSONResponse(
        status_code=400,
        content={"message": f"IllegalActionException: {str(exc)}"},
    )

from fastapi import FastAPI

from src.game_logic.board import Board
from src.game_logic.game import Game
from src.game_logic.player import Player


app = FastAPI()

board = Board.build_empty_board(10, 10)
players = [Player(10, i) for i in range(2)]
game = Game(board=board, players=players)


@app.get("/board")
async def root():
    return game.to_dict()

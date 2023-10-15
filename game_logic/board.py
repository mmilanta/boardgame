import json

from pydantic import BaseModel


class Board(BaseModel):
    height: int
    width: int

    def __init__(self, height: int, width: int) -> None:
        self.height = height
        self.width = width
        self.board = [[-1] * width for _ in range(height)]

    def serialize(self):
        out = self.board
        return json.dumps(out)


class Coord:
    row: int
    col: int
    board: Board

    def __init__(self, row, col, board: Board) -> None:
        self.board: Board = board
        self.row: int = row
        self.col: int = col
        self._check_bounds()

    def _check_bounds(
        self,
    ):
        if not (
            self.row >= 0
            and self.row <= self.board.height
            and self.col >= 0
            and self.col <= self.board.width
        ):
            raise ValueError("coordinate out of bounds")

    def distance(self, to) -> int:
        to._check_bounds()
        return max(abs(self.row - to.row), abs(self.col - to.col))

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Coord)
        return self.row == __value.row and self.col == __value.col

    def serialize(self):
        return {"row": self.row, "col": self.col}

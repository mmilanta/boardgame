from typing import List

from pydantic import BaseModel, ValidationError, field_validator


class Coord(BaseModel):
    row: int
    col: int

    def distance(self, to) -> int:
        return max(abs(self.row - to.row), abs(self.col - to.col))

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Coord)
        return self.row == __value.row and self.col == __value.col


class Board(BaseModel):
    raw_board: List[List[int]]

    @field_validator("raw_board")
    def raw_board_must_be_rectangular(cls, v):
        for row in v:
            if len(row) != len(v[0]):
                raise ValidationError("board must be rectangular")
        return v

    @staticmethod
    def build_empty(width: int, height: int) -> "Board":
        return Board(raw_board=[[-1] * width for _ in range(height)])

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Board)
        return self.raw_board == __value.raw_board

    @property
    def height(self):
        return len(self.raw_board)

    @property
    def width(self):
        return len(self.raw_board[0])

    def valid_coord(self, coord: Coord) -> bool:
        return 0 <= coord.col < self.width and 0 <= coord.row < self.height

from enum import Enum
from typing import List

from pydantic import BaseModel, ValidationError, model_validator

from src.game_logic.terrain_generation.perlin_noise import generate_world


class CellType(Enum):
    mauntain = "mauntain"
    plain = "plain"
    see = "see"
    empty = "empty"
    hills = "hills"
    city = "city"


class Cell(BaseModel):
    type: CellType
    yields: int


"""class Coord(BaseModel):
    row: int
    col: int

    def distance(self, to: 'Coord') -> int:
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
        return 0 <= coord.col < self.width and 0 <= coord.row < self.height"""


class HexCoord(BaseModel):
    q: int
    r: int
    s: int

    @model_validator(mode="after")
    def valid_params(self):
        if self.q + self.r + self.s != 0:
            raise ValidationError(
                "q,r,s coords must sum to 0."
                f"Sum to {self.q + self.r + self.s} instead"
            )
        return self

    def distance(self, to: "HexCoord") -> int:
        return max(
            [abs(self.q - to.q), abs(self.r - to.r), abs(self.s - to.s)]
        )

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, HexCoord)
        return (
            self.q == __value.q and self.r == __value.r and self.s == __value.s
        )


class HexBoard(BaseModel):
    raw_board: List[List[Cell]]
    radius: int

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, HexBoard)
        return self.raw_board == __value.raw_board

    @staticmethod
    def build_circular(radius: int) -> "HexBoard":
        side_size = (2 * radius) + 1

        type_from_idx = [
            CellType.see,
            CellType.plain,
            CellType.hills,
            CellType.mauntain,
        ]

        board_idxs = generate_world(side_size, side_size)
        raw_board = [
            [Cell(type=type_from_idx[idx], yields=1) for idx in row]
            for row in board_idxs
        ]

        # crop corners
        for row in range(radius):
            for i in range(radius - row):
                raw_board[row][i] = Cell(type=CellType.empty, yields=0)
                raw_board[side_size - 1 - row][side_size - 1 - i] = Cell(
                    type=CellType.empty, yields=0
                )

        return HexBoard(radius=radius, raw_board=raw_board)

    def valid_coord(self, coord: HexCoord) -> bool:
        for axis in [coord.q, coord.r, coord.s]:
            if abs(axis) > self.radius:
                return False
        return True

    def get_cell(self, coord: HexCoord) -> Cell:
        if not self.valid_coord(coord):
            raise OutOfBoardException()
        return self.raw_board[coord.q][coord.r]


class OutOfBoardException(Exception):
    pass

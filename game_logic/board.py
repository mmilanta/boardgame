from typing import Dict, List


class Board:
    def __init__(self, raw_board: List[List[int]]) -> None:
        self.raw_board = raw_board

    @property
    def height(self):
        return len(self.raw_board)

    @property
    def width(self):
        return len(self.raw_board[0])

    def to_dict(self):
        return self.raw_board

    @staticmethod
    def from_dict(dict_Board: List[List[int]]) -> "Board":
        return Board(dict_Board)

    @staticmethod
    def build_empty_board(width: int, height: int) -> "Board":
        return Board(raw_board=[[-1] * width for _ in range(height)])


class Coord:
    row: int
    col: int
    board: Board

    def __init__(self, row: int, col: int) -> None:
        self.row: int = row
        self.col: int = col

    def _check_bounds(self, board: Board):
        if not (
            self.row >= 0
            and self.row <= board.height
            and self.col >= 0
            and self.col <= board.width
        ):
            raise ValueError("coordinate out of bounds")

    def distance(self, to) -> int:
        to._check_bounds()
        return max(abs(self.row - to.row), abs(self.col - to.col))

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Coord)
        return self.row == __value.row and self.col == __value.col

    def to_dict(self):
        return {"row": self.row, "col": self.col}

    @staticmethod
    def from_dict(dict_Coord: Dict):
        return Coord(dict_Coord["row"], dict_Coord["col"])

    @staticmethod
    def from_row_col(row: int, col: int, board: Board):
        out = Coord(row, col)
        assert out._check_bounds(board)
        return out

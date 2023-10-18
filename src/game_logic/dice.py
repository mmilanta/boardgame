import logging
from random import randint
from typing import List

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class Dice(BaseModel):
    dice_size: int

    def roll(self) -> int:
        r = randint(1, self.dice_size)
        logger.info(f"dice of size {self.dice_size} rolled {r}")
        return r

    def expected(self) -> float:
        return (self.dice_size + 1) / 2

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Dice)
        return self.dice_size == __value.dice_size


class DiceSet(BaseModel):
    dices: List[Dice]

    def roll(self) -> int:
        out = 0
        for dice in self.dices:
            out += dice.roll()
        return out

    def expected(self) -> float:
        out = 0.0
        for dice in self.dices:
            out += dice.expected()
        return out

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, DiceSet)
        return self.dices == __value.dices

    @property
    def is_zero(self):
        return len(self.dices) == 0

    @staticmethod
    def from_dice_code(dice_code: str):
        dices = []
        if dice_code == "":
            return DiceSet(dices=[])
        dices_str = dice_code.split(" ")
        for dice in dices_str:
            n_dice_str, dice_size_str = dice.split("d")
            n_dice = 1 if n_dice_str == "" else int(n_dice_str)
            dice_size = int(dice_size_str)
            for _ in range(n_dice):
                dices.append(Dice(dice_size=dice_size))
        return DiceSet(dices=dices)

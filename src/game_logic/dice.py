from random import randint
from typing import Dict


class DiceSet:
    def __init__(self, dice_dictionary: Dict) -> None:
        self.dice_dictionary = dice_dictionary

    def roll(self):
        out = 0
        for dice_size in self.dice_dictionary:
            for _ in range(self.dice_dictionary[dice_size]):
                out += randint(1, dice_size)
        return out

    def expected(self):
        out = 0
        for dice_size in self.dice_dictionary:
            out += self.dice_dictionary[dice_size] * (dice_size + 1) / 2
        return out

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, DiceSet)
        return self.dice_dictionary == __value.dice_dictionary

    @property
    def is_zero(self):
        return len(self.dice_dictionary) == 0

    @staticmethod
    def from_dice_code(dice_code: str):
        dice_dictionary: Dict = {}
        if dice_code == "":
            return DiceSet(dice_dictionary)
        dices = dice_code.split(" ")
        for dice in dices:
            n_dice_str, dice_size_str = dice.split("d")
            n_dice = 1 if n_dice_str == "" else int(n_dice_str)
            dice_size = int(dice_size_str)
            dice_dictionary[dice_size] = n_dice
        return DiceSet(dice_dictionary)

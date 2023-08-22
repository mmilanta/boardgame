from random import randint


class DiceSet:
    def __init__(self, dice_dictionary: str) -> None:
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

    @property
    def is_zero(self):
        return len(self.dice_dictionary) == 0

    def from_dice_code(dice_code: str):
        dice_dictionary = {}
        if dice_code == "":
            return DiceSet(dice_dictionary)
        dices = dice_code.split(" ")
        for dice in dices:
            n_dice, dice_size = dice.split("d")
            n_dice = 1 if n_dice == "" else int(n_dice)
            dice_size = int(dice_size)
            dice_dictionary[dice_size] = n_dice
        return DiceSet(dice_dictionary)

from typing import Dict


class Player:
    id: int
    budget: int
    worker_to_place: bool

    def __init__(self, budget: int, id: int) -> None:
        self.budget: int = budget
        self.id: int = id
        self.worker_to_place: bool = True

    def reset_upkeep(self):
        self.worker_to_place = True

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Player)
        if self.id != __value.id:
            return False
        assert self.budget == __value.budget
        assert self.worker_to_place == __value.worker_to_place
        return True

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "budget": self.budget,
            "worker_to_place": self.worker_to_place,
        }

    @staticmethod
    def from_dict(dict_Player: Dict) -> "Player":
        out = Player(budget=dict_Player["budget"], id=dict_Player["id"])
        out.worker_to_place = dict_Player["worker_to_place"]
        return out

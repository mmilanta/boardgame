from pydantic import BaseModel


class Player(BaseModel):
    id: int
    budget: int
    worker_to_place: bool = True

    def reset_upkeep(self):
        self.worker_to_place = True

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, Player)
        if self.id != __value.id:
            return False
        assert self.budget == __value.budget
        assert self.worker_to_place == __value.worker_to_place
        return True

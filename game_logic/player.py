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
        return self.id == __value.id

    def serialize(self):
        return {"id": self.id, "budget": self.budget}

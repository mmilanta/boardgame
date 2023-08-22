
class Player:
    def __init__(self, budget, id) -> None:
        self.budget = budget
        self.worker_to_place = True
        self.id = id

    def reset_upkeep(self):
        self.worker_to_place = True

    def __eq__(self, __value: object) -> bool:
        return self.id == __value.id

    def serialize(self):
        return {"id": self.id, "budget": self.budget}

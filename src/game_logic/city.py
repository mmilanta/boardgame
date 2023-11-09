from pydantic import BaseModel, field_validator, ValidationError
from src.game_logic.board import HexCoord
from src.game_logic.units import Worker
from typing import List


class City(BaseModel):
    location: HexCoord
    owner_id: int
    id: int
    name: str = str(id)
    workers: List[Worker]
    actions: int = 0

    def __eq__(self, __value: object) -> bool:
        assert isinstance(__value, City)
        if self.id != __value.id:
            return False
        assert self.location == __value.location
        assert self.owner_id == __value.owner_id
        assert self.name == __value.name
        assert self.workers == __value.workers
        assert self.placed_worker == __value.placed_worker
        return True

    def reset_upkeep(self) -> int:
        self.actions = 1  # Can only create one unit or one worker per turn.
        yields = sum(worker.yields for worker in self.workers)
        return yields

    @field_validator("workers")
    def workers_close_to_city(cls, v: List[Worker], values):
        if not v:
            return v
        visited = [False] * len(v)

        search([w.location for w in v], visited, 0)

        # graph is connected
        for is_vis in visited:
            assert is_vis

        # graph is close to the city
        for pos in v:
            if pos.location.distance(values.data["location"]) <= 1:
                break
        else:
            raise ValidationError("Workers dont connect to the city")

        return v

    def is_worker_location_valid(self, location: HexCoord) -> bool:
        if location.distance(self.location) <= 1:
            return True
        for worker in self.workers:
            if location.distance(worker.location) <= 1:
                return True
        return False


def search(nodes: List[HexCoord], visited: List[bool], idx: int):
    if visited[idx]:
        return
    visited[idx] = True
    for j in range(len(nodes)):
        if nodes[j].distance(nodes[idx]) <= 1:
            search(nodes, visited, j)

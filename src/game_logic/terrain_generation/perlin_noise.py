from perlin_noise import PerlinNoise
from typing import List
OCTAVES = 3
THRESHOLDS = [-.1, 0, .2]


def generate_world(width: int, height: int):
    noise = PerlinNoise(octaves=OCTAVES)
    noise_discrete = [[noise([i / 10, j / 10]) for j in range(width)] for i in range(height)]

    def digitalize(elem: float, thresholds: List[float]):
        for i, th in enumerate(thresholds):
            if elem >= th:
                return i
        return len(thresholds)
    return [
        [digitalize(elem, THRESHOLDS) for elem in row] for row in noise_discrete
    ]

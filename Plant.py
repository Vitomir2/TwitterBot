from enum import Enum


class Plant:
    def __init__(self, positive, plant_name, partner_name, personality, sun_exposure, looks, size):
        self.positive = positive
        self.name = plant_name
        self.partner_name = partner_name
        self.personality = personality
        self.sun_exposure = sun_exposure
        self.looks = looks
        self.size = size


class Personality(Enum):
    Sensitive = 1
    Medium = 2
    Sturdy = 3


class SunExposure(Enum):
    Direct = 1
    Indirect = 2
    Indifferent = 3


class Size(Enum):
    Small = 1
    Medium = 2
    Huge = 3

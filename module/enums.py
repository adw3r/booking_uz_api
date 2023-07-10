from enum import Enum


class CityEnum(Enum):
    kyiv: str = '2200001'
    lviv: str = '2218000'


class WagonEnum(Enum):
    platskart: str = 'Плацкарт'
    kype: str = 'Купе'

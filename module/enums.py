import dataclasses
from datetime import datetime
from enum import Enum


class CityEnum(Enum):
    kyiv: str = '2200001'
    lviv: str = '2218000'


class WagonEnum(Enum):
    platskart: str = 'Плацкарт'
    kype: str = 'Купе'


class DateFormats(Enum):
    dep_format: str = '%Y-%m-%d'
    time_format: str = '%H:%M'


@dataclasses.dataclass(frozen=True, slots=True)
class DeparturePath:
    dep_from: CityEnum
    dep_to: CityEnum


@dataclasses.dataclass(frozen=True, slots=True)
class Departure:
    date: datetime
    path: DeparturePath
    acceptable_time: datetime

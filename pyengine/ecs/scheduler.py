from enum import Enum, auto
from typing import Dict, List
from pyengine.ecs.system import System
from pyengine.ecs.resource import ResourceManager


class SchedulerType(Enum):
    StartUp = 1
    Update = auto()
    Render = auto()


class SystemScheduler:
    def __init__(self):
        self._systems: Dict[SchedulerType, List[System]] = {}

    def add(self, scheduler: SchedulerType, system: System):
        if not scheduler in self._systems.keys():
            self._systems[scheduler] = []
        self._systems[scheduler].append(system)

    def execute(self, scheduler: SchedulerType, resources: ResourceManager):
        for system in self._systems.get(scheduler, []):
            system.update(resources)

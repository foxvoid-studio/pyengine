from pyengine.ecs.resource import ResourceManager
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyengine.core.app import App


class System(ABC):
    @abstractmethod
    def update(self, resources: ResourceManager): ...

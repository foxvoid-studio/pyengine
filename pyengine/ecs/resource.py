from abc import ABC
from typing import TypeVar, Type, Dict, Optional

class Resource(ABC): ...

R = TypeVar("R", bound=Resource)

class ResourceManager:
    def __init__(self):
        self._resources: Dict[Type[Resource], Resource] = {}

    def add(self, resource: Resource) -> None:
        self._resources[type(resource)] = resource

    def get(self, resource_type: Type[R]) -> Optional[R]:
        return self._resources.get(resource_type, None)

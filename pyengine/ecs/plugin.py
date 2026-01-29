from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyengine.core.app import App


class Plugin(ABC):
    @abstractmethod
    def build(self, app: 'App') -> None: ...

from __future__ import annotations
from abc import ABC, abstractmethod

from formatters import Registry

class SensitiveIdentifier(ABC):
    
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def identify_sensitive(self, registry : Registry) -> None:
        pass
    
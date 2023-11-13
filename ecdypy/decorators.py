from __future__ import annotations

""" Abstract Base Class """
from abc import ABC, abstractmethod

class Decorator(ABC):
    def __init__(self, *args) -> None:
        pass
    
    @abstractmethod
    def get_

    @abstractmethod
    def __str__(self) -> str:
        pass


class Derive(Decorator):
    pass
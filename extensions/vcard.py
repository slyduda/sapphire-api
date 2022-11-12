from typing import Mapping

URI = TypeVar('URI', str)

class VCardProperty():
    parameters: Mapping[str, set[str]]

    def __init__(self, name: str, value: list[list[str]]):
        self.property = property
        self.values = values
        self.parameters = {}

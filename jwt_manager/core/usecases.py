from abc import abstractmethod
from typing import Protocol


class TokenUseCase(Protocol):
    @abstractmethod
    def get_token(self) -> str:
        raise NotImplementedError

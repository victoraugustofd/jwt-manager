from abc import abstractmethod
from typing import Protocol, NoReturn


class TokenPort(Protocol):
    @abstractmethod
    def get_token(self) -> str:
        raise NotImplementedError


class CachePort(Protocol):
    @abstractmethod
    def cache_exists(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_cache_content(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def update_cache(self, token: str) -> NoReturn:
        raise NotImplementedError

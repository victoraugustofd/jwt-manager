import os
from datetime import datetime
from typing import Optional, NoReturn

import jwt
from dateutil.relativedelta import relativedelta
from trafalgar_log.core.logger import Logger

from jwt_manager.app import TOKEN, SETTINGS, CACHE_STRATEGIES
from jwt_manager.core.ports import TokenPort, CachePort
from jwt_manager.core.usecases import TokenUseCase
from jwt_manager.out.adapters import TokenAdapter

LOG_CODE = "Token Service"


def _define_cache_strategy():
    cache_strategy = CACHE_STRATEGIES.get(SETTINGS.get("CACHE_STRATEGY"))

    return cache_strategy()


class TokenService(TokenUseCase):
    _token_port: TokenPort = TokenAdapter()
    _cache_port: CachePort = _define_cache_strategy()

    def get_token(self) -> str:
        token: str
        token = self._get_cached_token()

        if not token or self._is_expired(token):
            token = self._generate_new_token()

        return token

    @classmethod
    def _get_cached_token(cls) -> str:
        token: str

        token = cls._get_token_from_env()

        if not token:
            token = cls._get_token_from_cache()

        return token

    @classmethod
    def _get_token_from_env(cls) -> str:
        Logger.info(LOG_CODE, "Searching token on environment variables.", "")

        return os.getenv(TOKEN)

    @classmethod
    def _get_token_from_cache(cls) -> Optional[str]:
        Logger.info(LOG_CODE, "Searching token on cache.", "")

        if cls._cache_port.cache_exists():
            return cls._cache_port.get_cache_content()

        return None

    @classmethod
    def _is_expired(cls, token: str) -> bool:
        Logger.info(LOG_CODE, "Checking if token is expired.", "")

        decoded_token = jwt.decode(
            jwt=token, options={"verify_signature": False}
        )

        return not decoded_token.get("exp") or cls._verify_expiration(
            decoded_token.get("exp")
        )

    @classmethod
    def _verify_expiration(cls, exp: str) -> bool:
        real_expiration_date = datetime.fromtimestamp(float(exp))
        expiration_date = real_expiration_date - relativedelta(
            seconds=SETTINGS.get("SAFETY_MARGIN_IN_SECONDS")
        )

        return expiration_date < datetime.now()

    @classmethod
    def _generate_new_token(cls) -> str:
        token = cls._token_port.get_token()

        cls._update_environment_variable(token)
        cls._update_cache(token)

        return token

    @classmethod
    def _update_environment_variable(cls, token) -> NoReturn:
        Logger.info(
            LOG_CODE,
            "Creating/updating token on environment variables.",
            "",
        )
        os.environ[TOKEN] = token

    @classmethod
    def _update_cache(cls, token: str) -> NoReturn:
        Logger.info(LOG_CODE, "Creating/updating token on cache.", "")
        cls._cache_port.update_cache(token)

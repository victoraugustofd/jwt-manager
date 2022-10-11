from requests import Response
from trafalgar_log.core.logger import Logger
from uplink import (
    Consumer,
    form_url_encoded,
    post,
    Field,
    error_handler,
    response_handler,
)

from jwt_manager.app import SETTINGS
from jwt_manager.core.exceptions import TokenGenerationException

LOG_CODE = "Token Client"


def raise_for_status(response: Response) -> str:
    status_code: int = response.status_code

    if _is_success(status_code):
        Logger.info(LOG_CODE, "Successfully generated token.", response)
        return response.json().get("access_token")
    else:
        Logger.error(LOG_CODE, "Fail to generate token.", response)
        raise TokenGenerationException(response.json())


def raise_api_error(exc_type, exc_val, exc_tb):
    Logger.error(LOG_CODE, "Fail to generate token.", exc_val)
    raise TokenGenerationException(exc_val)


def _is_success(status_code: int):
    return 200 <= status_code < 300


@error_handler(raise_api_error)
class TokenClient(Consumer):
    @response_handler(raise_for_status)
    @form_url_encoded
    @post(SETTINGS.get("ENDPOINT"))
    def get_token(
        self,
        grant_type: Field = "client_credentials",
        client_id: Field = SETTINGS.get("CLIENT_ID"),
        client_secret: Field = SETTINGS.get("CLIENT_SECRET"),
        audience: Field = SETTINGS.get("AUDIENCE"),
    ) -> str:
        """Generate new token."""

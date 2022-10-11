from dynaconf import Validator, Dynaconf, ValidationError

from jwt_manager.core.exceptions import ConfigurationException


TOKEN = "TOKEN"
SETTINGS = Dynaconf(
    envvar_prefix="JWT_MANAGER",
    load_dotenv=True,
    validators=[
        Validator(
            "URL",
            "ENDPOINT",
            "CLIENT_ID",
            "CLIENT_SECRET",
            "S3_BUCKET",
            must_exist=True,
        ),
        Validator("CACHE_STRATEGY", default="s3"),
        Validator("SAFETY_MARGIN_IN_SECONDS", must_exist=True, default=30),
        Validator("AUDIENCE"),
        Validator("AWS_ENDPOINT", must_exist=True, env="local"),
    ],
)

try:
    SETTINGS.validators.validate_all()
except ValidationError as e:
    raise ConfigurationException()

from jwt_manager.out.adapters import S3Adapter

CACHE_STRATEGIES: dict = {"s3": S3Adapter}

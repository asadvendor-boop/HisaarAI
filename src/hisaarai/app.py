"""Production ASGI entrypoint."""

from hisaarai.app_factory import create_app


app = create_app()

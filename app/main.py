from starlette.types import ASGIApp

from api.http import http_api
from utility.decorator import singleton


@singleton
class HTTP_API:
    def __init__(self, app: ASGIApp):
        self.app = app


http_api_app: ASGIApp = HTTP_API(http_api).app

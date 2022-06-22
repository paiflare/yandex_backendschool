import logging
from types import MappingProxyType
from typing import Mapping

from aiohttp import PAYLOAD_REGISTRY
from aiohttp.web_app import Application
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

from price_comparison.api.handlers import HANDLERS
from price_comparison.api.middleware import (
    error_middleware,
    handle_validation_error,
)
from price_comparison.api.payloads import JsonPayload
from price_comparison.utils.pg import setup_pg

# По умолчанию размер запроса к aiohttp ограничен 1 мегабайтом:
# https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application
MEGABYTE = 1024 ** 2
MAX_REQUEST_SIZE = 70 * MEGABYTE

log = logging.getLogger(__name__)


def create_app() -> Application:
    """
    Создает экземпляр приложения, готового к запуску.
    """
    app = Application(
        client_max_size=MAX_REQUEST_SIZE,
        middlewares=[error_middleware, validation_middleware],
    )

    # Подключение на старте к postgres и отключение при остановке
    app.cleanup_ctx.append(setup_pg)

    # Регистрация обработчиков
    for handler in HANDLERS:
        log.debug('Registering handler %r as %r', handler, handler.URL_PATH)
        app.router.add_route('*', handler.URL_PATH, handler)

    # Swagger документация
    setup_aiohttp_apispec(
        app=app,
        title='price comparison API',
        swagger_path='/',
        error_callback=handle_validation_error,
    )

    # Автоматическая сериализация в json данных в HTTP ответах
    PAYLOAD_REGISTRY.register(JsonPayload, (Mapping, MappingProxyType))
    return app

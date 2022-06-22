import logging
from pathlib import Path

from aiohttp.web_app import Application
from asyncpgsa import PG
from sqlalchemy import Numeric, cast, func

from price_comparison.config import conf

MAX_QUERY_ARGS = 32767
MAX_INTEGER = 2147483647
PROJECT_PATH = Path(__file__).parent.parent.resolve()


log = logging.getLogger(__name__)


async def setup_pg(app: Application) -> PG:
    log.info('Connecting to database: %s', conf.name)

    app['pg'] = PG()
    await app['pg'].init(
        str(conf.url),
        min_size=conf.options.min_size,
        max_size=conf.options.max_size,
    )
    await app['pg'].fetchval('SELECT 1')
    log.info('Connected to database %s', conf.name)

    try:
        yield
    finally:
        log.info('Disconnecting from database %s', conf.name)
        await app['pg'].pool.close()
        log.info('Disconnected from database %s', conf.name)


def rounded(column, fraction: int = 2):
    return func.round(cast(column, Numeric), fraction)

from decouple import config
from pydantic import BaseModel


class DbOptions(BaseModel):
    min_size: int
    max_size: int
    statement_cache_size: int = 0


class DbConf(BaseModel):
    name: str
    url: str
    options: DbOptions


conf = DbConf(
    name=config('POSTGRES_DB'),
    url='postgresql://{0}:{1}@db:5432/{2}'.format(
        config('POSTGRES_USER'),
        config('POSTGRES_PASSWORD'),
        config('POSTGRES_DB'),
    ),
    options=DbOptions(min_size=config('DB_MIN'), max_size=config('DB_MAX')),
)

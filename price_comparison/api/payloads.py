import json
from datetime import datetime
from decimal import Decimal
from functools import partial, singledispatch
from typing import Any
from uuid import UUID

from aiohttp.payload import JsonPayload as BaseJsonPayload
from aiohttp.typedefs import JSONEncoder
from asyncpg import Record

from price_comparison.api.schema import DATETIME_FORMAT


@singledispatch
def convert(value):
    """
    Модуль json позволяет указать функцию, которая будет вызываться для
    обработки не сериализуемых в JSON объектов. Функция должна вернуть либо
    сериализуемое в JSON значение, либо исключение TypeError:
    https://docs.python.org/3/library/json.html#json.dump
    """
    raise TypeError(f'Unserializable value: {value!r}')


@convert.register(Record)
def convert_asyncpg_record(value: Record):
    """
    Позволяет автоматически сериализовать результаты запроса, возвращаемые
    asyncpg.
    """
    return dict(value)


@convert.register(datetime)
def convert_date(value: datetime):
    return value.strftime(DATETIME_FORMAT)


@convert.register(Decimal)
def convert_decimal(value: Decimal):
    """
    asyncpg возвращает округленные перцентили возвращаются виде экземпляров
    класса Decimal.
    """
    return float(value)


@convert.register(UUID)
def convert_uuid(value: UUID):
    return str(value)


dumps = partial(json.dumps, default=convert, ensure_ascii=False)


class JsonPayload(BaseJsonPayload):
    """
    Заменяет функцию сериализации на более "умную" (умеющую упаковывать в JSON
    объекты asyncpg.Record и другие сущности).
    """
    def __init__(
        self,
        value: Any,
        encoding: str = 'utf-8',
        content_type: str = 'application/json',
        dumps: JSONEncoder = dumps,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(value, encoding, content_type, dumps, *args, **kwargs)


__all__ = (
    'JsonPayload'
)

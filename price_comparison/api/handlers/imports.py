from http import HTTPStatus
from typing import Dict, Generator

from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema, response_schema
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert

from price_comparison.api.handlers.base import BaseView
from price_comparison.api.schema import Error, ShopUnitImportRequest
from price_comparison.db.schema import shop_unit_table


class ImportsView(BaseView):
    URL_PATH = '/imports'

    @classmethod
    def make_shop_unit_table_rows(cls, shop_units, update_date) -> Generator[Dict[str, str], None, None]:
        for shop_unit in shop_units:
            yield {
                'id': shop_unit['id'],
                'name': shop_unit['name'],
                'date': update_date,
                'parentId': shop_unit.get('parentId', None),
                'type': shop_unit['type'],
                'price': shop_unit.get('price', None),
            }

    async def get_all_parents(self, shop_unit):
        while True:
            query = shop_unit_table.select().where(shop_unit_table.c.id == shop_unit.get('parentId'))
            shop_unit = await self.pg.fetchrow(query)

            if not shop_unit:
                break

            yield shop_unit

    @docs(summary='Добавить выгрузку с информацией об items')
    @request_schema(ShopUnitImportRequest())
    @response_schema(Error(), code=HTTPStatus.BAD_REQUEST.value)
    async def post(self):
        async with self.pg.transaction() as conn:
            items = self.request['data']['items']
            update_date = self.request['data']['updateDate']

            shop_unit_rows = self.make_shop_unit_table_rows(items, update_date)

            query = insert(shop_unit_table)
            for shop_unit in shop_unit_rows:
                insert_stmt = query.values(shop_unit)
                do_update_stmt = insert_stmt.on_conflict_do_update(
                    constraint='pk__shop_unit',
                    set_=shop_unit,
                )
                await conn.execute(do_update_stmt)

                async for shop_unit_parent in self.get_all_parents(shop_unit):
                    update_query = update(shop_unit_table).\
                        where(shop_unit_table.c.id==shop_unit_parent.get('id')).\
                            values(date=update_date)
                    await conn.execute(update_query)

        return Response(status=HTTPStatus.OK)

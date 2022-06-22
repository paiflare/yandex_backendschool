from http import HTTPStatus
from uuid import UUID

from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema
from marshmallow import ValidationError
from sqlalchemy import select

from price_comparison.api.handlers.base import BaseView
from price_comparison.api.schema import Error
from price_comparison.db.schema import shop_unit_table


class DeleteView(BaseView):
    URL_PATH = '/delete/{id}'

    @property
    def id(self):
        try:
            id = UUID(self.request.match_info.get('id'))
        except ValueError as err:
            raise ValidationError('badly formed hexadecimal UUID string')

        return id

    async def get_all_childrens(self, shop_unit_id):
        query = select([shop_unit_table.c.id]).where(shop_unit_table.c.parentId == shop_unit_id)
        shop_unit_id_childrens = await self.pg.fetch(query)

        ids = set()

        for children in shop_unit_id_childrens:
            children_id = children.get('id')
            childrens_ids = await self.get_all_childrens(children_id)

            ids.update(childrens_ids)
        else:
            ids.update(set([shop_unit_id]))
            return ids

    @docs(summary='Удалить элемент с указанным id и все дочерние')
    @response_schema(Error(), code=HTTPStatus.BAD_REQUEST.value)
    @response_schema(Error(), code=HTTPStatus.NOT_FOUND.value)
    async def delete(self):
        query = select([shop_unit_table.c.id]).where(shop_unit_table.c.id == self.id)
        shop_unit_id = await self.pg.fetchrow(query)

        if not shop_unit_id:
            raise HTTPNotFound(text='Item not found')

        ids = await self.get_all_childrens(shop_unit_id.get('id'))

        async with self.pg.transaction() as conn:
            query = shop_unit_table.delete()
            for del_id in ids:
                await conn.execute(query.where(shop_unit_table.c.id == del_id))

        return Response(status=HTTPStatus.OK)

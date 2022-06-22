from http import HTTPStatus
from uuid import UUID

from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_response import Response
from aiohttp_apispec import docs, response_schema
from marshmallow import ValidationError
from sqlalchemy import select

from price_comparison.api.handlers.base import BaseView
from price_comparison.api.schema import Error, ShopUnit, ShopUnitTypeEnum
from price_comparison.db.schema import shop_unit_table


class NodesView(BaseView):
    URL_PATH = '/nodes/{id}'

    @property
    def id(self):
        try:
            id = UUID(self.request.match_info.get('id'))
        except ValueError as err:
            raise ValidationError('badly formed hexadecimal UUID string')

        return id

    async def get_all_childrens(self, shop_unit):
        shop_unit_dict = dict(shop_unit)
        shop_unit_dict['date'] = shop_unit.get('date').isoformat(timespec='milliseconds') + 'Z'

        shop_unit_type = shop_unit.get('type')
        if shop_unit_type == ShopUnitTypeEnum.OFFER.value:
            shop_unit_dict['children'] = None
            S = shop_unit.get('price')
            cnt = 1
        elif shop_unit_type == ShopUnitTypeEnum.CATEGORY.value:
            shop_unit_dict['children'] = list()
            S = 0
            cnt = 0

        query = shop_unit_table.select().where(shop_unit_table.c.parentId == shop_unit.get('id'))
        shop_unit_childrens = await self.pg.fetch(query)

        for children in shop_unit_childrens:
            his_children, S_children, cnt_children = await self.get_all_childrens(children)
            shop_unit_dict['children'].append(his_children)
            S += S_children
            cnt += cnt_children
        else:
            if shop_unit_type == ShopUnitTypeEnum.CATEGORY.value and cnt != 0:
                shop_unit_dict['price'] = int(S / cnt)
            return shop_unit_dict, S, cnt

    @docs(summary='Вернуть элемент с указанным id и все дочерние')
    @response_schema(ShopUnit(), code=HTTPStatus.OK.value)
    @response_schema(Error(), code=HTTPStatus.BAD_REQUEST.value)
    @response_schema(Error(), code=HTTPStatus.NOT_FOUND.value)
    async def get(self):
        query = select(shop_unit_table.columns).where(shop_unit_table.c.id==self.id)
        shop_unit = await self.pg.fetchrow(query)

        if not shop_unit:
            raise HTTPNotFound(text='Item not found')

        result, S, cnt = await self.get_all_childrens(shop_unit)

        return Response(status=HTTPStatus.OK, body=result)

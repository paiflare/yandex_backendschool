from datetime import timedelta
from http import HTTPStatus

from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema, response_schema
from sqlalchemy import select

from price_comparison.api.handlers.base import BaseView
from price_comparison.api.schema import Date, Error, ShopUnitStatisticResponse, ShopUnitTypeEnum
from price_comparison.db.schema import shop_unit_table


class StatisticView(BaseView):
    URL_PATH = '/sales'

    @docs(summary='Вернуть список товаров с обновленным price за 24 от времени в запросе')
    @request_schema(Date())
    @response_schema(ShopUnitStatisticResponse(), code=HTTPStatus.OK.value)
    @response_schema(Error(), code=HTTPStatus.BAD_REQUEST.value)
    async def get(self):
        date_end = self.request['data']['date']
        date_start = date_end - timedelta(hours=24)

        query = select(shop_unit_table.columns).\
            where((shop_unit_table.c.type==ShopUnitTypeEnum.OFFER.value) &
                  (shop_unit_table.c.date>=date_start) &
                  (shop_unit_table.c.date<=date_end))
        items = await self.pg.fetch(query)

        return Response(status=HTTPStatus.OK, body={'items': items})

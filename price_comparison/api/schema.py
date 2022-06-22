from datetime import datetime
from enum import Enum, unique

from marshmallow import Schema, ValidationError, validates, validates_schema
from marshmallow.fields import UUID, DateTime, Int, Nested, Str
from marshmallow.validate import Length, OneOf, Range
from marshmallow_enum import EnumField

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


@unique
class ShopUnitTypeEnum(Enum):
    OFFER = 'OFFER'
    CATEGORY = 'CATEGORY'


class ShopUnitType(Schema):
    enum = EnumField(ShopUnitTypeEnum)


class PatchShopUnit(Schema):
    id = UUID(strict=True, required=True)
    name = Str(validate=Length(min=1, max=256), allow_none=False, strict=True, required=True)
    parentId = UUID(allow_none=True, strict=True)
    price = Int(validate=Range(0), allow_none=True, strict=True)
    type = EnumField(ShopUnitTypeEnum, by_value=True, strict=True, required=True)


class ShopUnit(PatchShopUnit):
    date = DateTime(format=DATETIME_FORMAT, strict=True, required=True)
    children = Nested(lambda: ShopUnit(), allow_none=True, required=True)


class ShopUnitImport(PatchShopUnit):
    @validates_schema
    def validate_price(self, data, **kwargs):
        if data['type'] == ShopUnitTypeEnum.CATEGORY:
            if data.get('price', None) is not None:
                raise ValidationError('category price must be null')
        elif data['type'] == ShopUnitTypeEnum.OFFER:
            if data.get('price', None) is None:
                raise ValidationError('offer price cant be null')


class ShopUnitImportRequest(Schema):
    items = Nested(
        ShopUnitImport,
        many=True,
        required=True,
        validate=Length(max=10000),
    )
    updateDate = DateTime(format=DATETIME_FORMAT, strict=True, required=True)

    @validates('updateDate')
    def validate_date(self, value: datetime):
        if value > datetime.today():
            raise ValidationError("date can't be in future")

    @validates_schema
    def validate_unique_shop_unit_id(self, data, **kwargs):
        shop_unit_ids = set()
        for shop_unit in data['items']:
            if shop_unit['id'] in shop_unit_ids:
                raise ValidationError('id %r is not unique' % shop_unit['id'])
            shop_unit_ids.add(shop_unit['id'])


class Error(Schema):
    code = Int(allow_none=False, strict=True, required=True)
    message = Str(allow_none=False, strict=True, required=True)

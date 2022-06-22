from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as PgEnum
from sqlalchemy import Integer, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID

from price_comparison.api.schema import ShopUnitTypeEnum

convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),

    # Именование индексов
    'ix': 'ix__%(table_name)s__%(all_column_names)s',

    # Именование уникальных индексов
    'uq': 'uq__%(table_name)s__%(all_column_names)s',

    # Именование CHECK-constraint-ов
    'ck': 'ck__%(table_name)s__%(constraint_name)s',

    # Именование внешних ключей
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',

    # Именование первичных ключей
    'pk': 'pk__%(table_name)s',
}
metadata = MetaData(naming_convention=convention)


shop_unit_table = Table(
    'shop_unit',
    metadata,
    Column('id', UUID, primary_key=True),
    Column('name', String, nullable=False),
    Column('date', DateTime(timezone=False), nullable=False),
    Column('parentId', UUID, nullable=True, index=True),
    Column('type', PgEnum(ShopUnitTypeEnum, name='shop_unit_type'), nullable=False),
    Column('price', Integer, nullable=True),
)

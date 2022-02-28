import datetime
from typing import Optional
from sqlalchemy.sql.schema import Table, MetaData
from sqlalchemy.ext.declarative import as_declarative, declared_attr


TYPE_NEED_QUOTE = (
    str,
    datetime.datetime,
    datetime.date,
    datetime.time
)


@as_declarative()
class Base:
    id: Optional[int]
    __name__: str # for __tablename__ classmethod
    __table__: Table # for automatic __repr__
    metadata: MetaData # for create_table

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        keys = self.__table__.columns.keys()
        one_row = len(keys) <= 5
        return self._make_repr(keys, one_row=one_row)

    def _make_repr(self, keys, one_row=True, sep_kv="=", indent="    "):
        """
        keys: the instance's attributes you want to present
        one_row: repr in one row or not (True by default),
                 if set True, then ignore `indent` parameter
        """
        if one_row:
            indent = ""
        sep_row = " " if one_row else "\n"
        attr_lst = []
        for key in keys:
            val = getattr(self, key, None)
            if isinstance(val, TYPE_NEED_QUOTE):
                tmp = '{}{}{}"{}"'
            else:
                tmp = '{}{}{}{}'
            attr_lst.append(tmp.format(indent, key, sep_kv, val))
        attr_str = ("," + sep_row).join(attr_lst)
        return sep_row.join([f"{self.__class__.__name__} {{", attr_str, "}"])

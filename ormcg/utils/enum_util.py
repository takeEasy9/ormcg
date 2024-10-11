# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: enum
@version: 1.0.0
@since: 2024/4/30 19:30
"""
from enum import Enum, unique


class EnumBase(str, Enum):
    """ enum base class """

    def __new__(cls, value, label: str):
        obj = str.__new__(cls, [str(value)])
        obj._value_ = value
        obj._label_ = label
        return obj

    def get_value(self):
        return self._value_

    def get_label(self):
        return self._label_

    @classmethod
    def is_exist(cls, value):
        values = set(item.value for item in cls)
        return value in values


class OrmCgEnum:
    """orm code generator enum """

    @unique
    class ORM(EnumBase):
        """ ORM  """
        ORM_MYBATIS = ('mybatis', 'mybatis')

        ORM_JPA = ('jpa', 'jpa')

    @unique
    class CrudType(EnumBase):
        """ Database operation type """
        CRUD_TYPE_INSERT = ('1', 'insert')

        CRUD_TYPE_UPDATE = ('2', 'update')

        CRUD_TYPE_SELECT = ('3', 'select')

    @unique
    class CrudSubType(EnumBase):
        """ Database operation subtype  """
        CRUD_SUB_TYPE_INSERT_DYNAMICAL = ('11', 'dynamically insert')

        CRUD_SUB_TYPE_INSERT_USUAL = ('12', 'usually insert')

        CRUD_SUB_TYPE_INSERT_BATCH = ('13', 'batch insert')

        CRUD_SUB_TYPE_UPDATE_DYNAMICAL = ('21', 'dynamically update')

        CRUD_SUB_TYPE_UPDATE_USUAL = ('22', 'usually update')

        CRUD_SUB_TYPE_SELECT_BY_DYNAMICAL_CONDITION = ('31', 'query by dynamical condition')

        CRUD_SUB_TYPE_SELECT_BY_UNIQUE_KEYS = ('32', 'query by unique key')

        CRUD_SUB_TYPE_SELECT_LIKE_QUERY = ('33', 'like query')

    @unique
    class EntityPropertyType(EnumBase):
        """ java entity property type """
        # String
        ENTITY_PROPERTY_TYPE_STING = ('1', 'String')
        # Number
        ENTITY_PROPERTY_TYPE_NUMERICAL = ('2', 'Number ')
        # Other
        ENTITY_PROPERTY_TYPE_OTHER = ('3', 'Other')

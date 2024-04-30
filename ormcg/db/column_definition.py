# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: db table column info entity
@version: 1.0.0
@since: 2024/4/30 19:58
"""


class ColumnDefinition:

    def __init__(self, **kwargs):
        # column name all lowercase letters
        self.column_name = kwargs.get('column_name', None)
        self.column_comment = kwargs.get('column_comment', None)
        # database data type
        self.column_data_type = kwargs.get('column_data_type', None)
        # index type like PRI UNIQUE KEY
        self.column_key_type = kwargs.get('column_key_type', None)
        # 单个列是否是唯一的, 如主键、单个列的唯一索引
        self.column_single_unique = kwargs.get('column_single_unique', False)
        # camel case field name
        self.field_name = kwargs.get('field_name', None)
        # entity super class
        self.field_inherited = kwargs.get('field_inherited', False)
        self.field_type = kwargs.get('field_type', None)
        # java type import flag
        self.import_flag = kwargs.get('import_flag', False)
        # java type package like java.util.String
        self.field_type_with_package = kwargs.get('field_type_with_package', None)
        # field get method
        self.field_getter = kwargs.get('field_getter', None)
        # field set method
        self.field_setter = kwargs.get('field_setter', None)
        # The corresponding jdbc_type for the column
        self.jdbc_type = kwargs.get('jdbc_type', None)
        self.column_order = kwargs.get('column_order', 1)
        self.char_max_length = kwargs.get('char_max_length', None)
        self.numeric_precision = kwargs.get('numeric_precision', None)
        self.numeric_scale = kwargs.get('numeric_scale', None)

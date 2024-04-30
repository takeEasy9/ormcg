# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: mysql information schema models
@version: 1.0.0
@since: 2024/4/30 19:55
"""

from sqlalchemy import Column, String, BINARY, Enum, Integer, BigInteger, TIMESTAMP, DateTime, Text, \
    PrimaryKeyConstraint, Boolean
from sqlalchemy.dialects import mysql
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import declarative_base

# base class
_Base_Model = declarative_base()


class MysqlSchemataModel(_Base_Model):
    __tablename__ = 'SCHEMATA'
    catalog_name = Column('CATALOG_NAME', String(length=64), nullable=False)
    schema_name = Column('SCHEMA_NAME', String(length=64), primary_key=True, nullable=False)
    default_character_set_name = Column('DEFAULT_CHARACTER_SET_NAME', String(length=64), nullable=False)
    default_collation_name = Column('DEFAULT_COLLATION_NAME', String(length=64), nullable=False)
    sql_path = Column('SQL_PATH', BINARY(length=0), nullable=True)
    default_encryption = Column('DEFAULT_ENCRYPTION', Enum('NO', 'YES'), nullable=False)

    def __str__(self):
        return 'mysql_information_schema_models.MysqlSchemataModel{' \
               + f'catalog_name={self.catalog_name}' \
               + f', schema_name={self.schema_name}' \
               + f', default_character_set_name={self.default_character_set_name}' \
               + f', default_collation_name={self.default_collation_name}' \
               + '}'


class MysqlTablesModel(_Base_Model):
    __tablename__ = 'TABLES'
    __table_args__ = (PrimaryKeyConstraint('TABLE_SCHEMA', 'TABLE_NAME', name='pk_table_name'),)
    table_catalog = Column('TABLE_CATALOG', String(length=64), nullable=False)
    table_schema = Column('TABLE_SCHEMA', String(length=64), nullable=False)
    table_name = Column('TABLE_NAME', String(length=64), nullable=False)
    table_type = Column('TABLE_TYPE', Enum('BASE TABLE', 'VIEW', 'SYSTEM VIEW'), nullable=False)
    engine = Column('ENGINE', String(length=64), nullable=True)
    version = Column('VERSION', Integer, nullable=True)
    row_format = Column('ROW_FORMAT', Enum('Fixed', 'Dynamic', 'Compressed', 'Redundant', 'Compact', 'Paged'),
                        nullable=True)
    table_rows = Column('TABLE_ROWS', BigInteger, nullable=True)
    avg_row_length = Column('AVG_ROW_LENGTH', BigInteger, nullable=True)
    data_length = Column('DATA_LENGTH', BigInteger, nullable=True)
    max_data_length = Column('MAX_DATA_LENGTH', BigInteger, nullable=True)
    index_length = Column('INDEX_LENGTH', BigInteger, nullable=True)
    data_free = Column('DATA_FREE', BigInteger, nullable=True)
    auto_increment = Column('AUTO_INCREMENT', BigInteger, nullable=True)
    create_time = Column('CREATE_TIME', TIMESTAMP(timezone=True), nullable=False)
    update_time = Column('UPDATE_TIME', DateTime, nullable=True)
    check_time = Column('CHECK_TIME', DateTime, nullable=True)
    table_collation = Column('TABLE_COLLATION', String(length=64), nullable=True)
    checksum = Column('CHECKSUM', BigInteger, nullable=True)
    create_options = Column('CREATE_OPTIONS', String(length=256), nullable=True)
    table_comment = Column('TABLE_COMMENT', Text, nullable=True)

    def __str__(self):
        return 'mysql_information_schema_models.MysqlTablesModel{' \
               + f'table_catalog={self.table_catalog}' \
               + f', table_schema={self.table_schema}' \
               + f', table_name={self.table_name}' \
               + f', engine={self.engine}' \
               + f', row_format={self.row_format}' \
               + f', table_rows={self.table_rows}' \
               + f', avg_row_length={self.avg_row_length}' \
               + f', data_length={self.data_length}' \
               + f', max_data_length={self.max_data_length}' \
               + f', data_free={self.data_free}' \
               + f', auto_increment={self.auto_increment}' \
               + f', create_time={self.create_time}' \
               + f', update_time={self.update_time}' \
               + f', check_time={self.check_time}' \
               + f', table_collation={self.table_collation}' \
               + f', checksum={self.checksum}' \
               + f', create_options={self.create_options}' \
               + f', table_comment={self.table_comment}' \
               + '}'


class MysqlColumnsModel(_Base_Model):
    __tablename__ = 'COLUMNS'
    __table_args__ = (PrimaryKeyConstraint('TABLE_SCHEMA', 'TABLE_NAME', 'COLUMN_NAME', name='pk_column_name'),)
    table_catalog = Column('TABLE_CATALOG', String(length=64), nullable=False)
    table_schema = Column('TABLE_SCHEMA', String(length=64), nullable=False)
    table_name = Column('TABLE_NAME', String(length=64), nullable=False)
    column_name = Column('COLUMN_NAME', String(length=64), nullable=True)
    ordinal_position = Column('ORDINAL_POSITION', Integer, nullable=False)
    column_default = Column('COLUMN_DEFAULT', Text, nullable=True)
    is_nullable = Column('IS_NULLABLE', String(length=64), nullable=False)
    data_type = Column('DATA_TYPE', LONGTEXT, nullable=True)
    character_maximum_length = Column('CHARACTER_MAXIMUM_LENGTH', BigInteger, nullable=True)
    character_octet_length = Column('CHARACTER_OCTET_LENGTH', BigInteger, nullable=True)
    numeric_precision = Column('NUMERIC_PRECISION', BigInteger, nullable=True)
    numeric_scale = Column('NUMERIC_SCALE', BigInteger, nullable=True)
    datetime_precision = Column('DATETIME_PRECISION', Integer, nullable=True)
    character_set_name = Column('CHARACTER_SET_NAME', String(length=64), nullable=True)
    collation_name = Column('COLLATION_NAME', String(length=64), nullable=True)
    column_type = Column('COLUMN_TYPE', mysql.MEDIUMTEXT, nullable=False)
    column_key = Column('COLUMN_KEY', Enum('', 'PRI', 'UNI', 'MUL'), nullable=False)
    extra = Column('EXTRA', String(length=256), nullable=True)
    privileges = Column('PRIVILEGES', String(length=154), nullable=True)
    column_comment = Column('COLUMN_COMMENT', Text, nullable=False)
    generation_expression = Column('GENERATION_EXPRESSION', LONGTEXT, nullable=False)
    srs_id = Column('SRS_ID', Integer, nullable=True)

    def __str__(self):
        return 'mysql_information_schema_models.MysqlColumnsModel{' \
               + f'table_catalog={self.table_catalog}' \
               + f', table_schema={self.table_schema}' \
               + f', table_name={self.table_name}' \
               + f', column_name={self.column_name}' \
               + f', ordinal_position={self.ordinal_position}' \
               + f', column_default={self.column_default}' \
               + f', is_nullable={self.is_nullable}' \
               + f', data_type={self.data_type}' \
               + f', character_maximum_length={self.character_maximum_length}' \
               + f', character_octet_length={self.character_octet_length}' \
               + f', numeric_precision={self.numeric_precision}' \
               + f', numeric_scale={self.numeric_scale}' \
               + f', datetime_precision={self.datetime_precision}' \
               + f', character_set_name={self.character_set_name}' \
               + f', collation_name={self.collation_name}' \
               + f', column_type={self.column_type}' \
               + f', column_key={self.column_key}' \
               + f', extra={self.extra}' \
               + f', privileges={self.privileges}' \
               + f', column_comment={self.column_comment}' \
               + f', generation_expression={self.generation_expression}' \
               + f', srs_id={self.srs_id}' \
               + '}'


class MysqlStatisticsModel(_Base_Model):
    __tablename__ = 'STATISTICS'
    __table_args__ = (PrimaryKeyConstraint('TABLE_SCHEMA', 'TABLE_NAME', 'INDEX_NAME', 'COLUMN_NAME', name='pk_tb_index_name'),)
    table_catalog = Column('TABLE_CATALOG', String(length=64), nullable=False)
    table_schema = Column('TABLE_SCHEMA', String(length=64), nullable=False)
    table_name = Column('TABLE_NAME', String(length=64), nullable=False)
    non_unique = Column('NON_UNIQUE', Integer, nullable=False)
    index_schema = Column('INDEX_SCHEMA', String(length=64), nullable=False)
    index_name = Column('INDEX_NAME', String(length=64), nullable=True)
    seq_in_index = Column('SEQ_IN_INDEX', Integer, nullable=False)
    column_name = Column('COLUMN_NAME', String(length=64), nullable=True)
    collation = Column('COLLATION', String(length=64), nullable=True)
    cardinality = Column('CARDINALITY', BigInteger, nullable=True)
    sub_part = Column('SUB_PART', BigInteger, nullable=True)
    packed = Column('PACKED', Boolean, nullable=True)
    nullable = Column('NULLABLE', String(length=3), nullable=False)
    index_type = Column('INDEX_TYPE', String(length=11), nullable=False)
    comment = Column('COMMENT', String(length=8), nullable=False)
    index_comment = Column('INDEX_COMMENT', String(length=2048), nullable=False)
    is_visible = Column('IS_VISIBLE', String(length=3), nullable=False)
    expression = Column('EXPRESSION', Text, nullable=True)

    def __str__(self):
        return 'mysql_information_schema_models.MysqlStatisticsModel{' \
               + f'table_catalog={self.table_catalog}' \
               + f', table_schema={self.table_schema}' \
               + f', table_name={self.table_name}' \
               + f', non_unique={self.non_unique}' \
               + f', index_schema={self.index_schema}' \
               + f', index_name={self.index_name}' \
               + f', seq_in_index={self.seq_in_index}' \
               + f', column_name={self.column_name}' \
               + f', collation={self.collation}' \
               + f', cardinality={self.cardinality}' \
               + f', sub_part={self.sub_part}' \
               + f', packed={self.packed}' \
               + f', nullable={self.nullable}' \
               + f', index_type={self.index_type}' \
               + f', comment={self.comment}' \
               + f', index_comment={self.index_comment}' \
               + f', is_visible={self.is_visible}' \
               + f', expression={self.expression}' \
               + '}'

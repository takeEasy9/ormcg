# -*- coding: utf-8 -*-

"""
@author takeEasy9
@version 1.0.0
@since 1.0.0
@description jpa generator
@createDate 2024/10/11 13:40
"""
import datetime

from ormcg.config.logger_config import logger
from ormcg.core.orm_generator import java_import_sort
from ormcg.db.column_definition import ColumnDefinition
from ormcg.utils.constant_util import ConstantUtil
from ormcg.utils.file_util import write_file
from ormcg.utils.string_util import first_upper_case

"""R2dbcRepository, CrudRepository"""


def get_find_by_unique_keys(schema, table, entity_name, cds: list[ColumnDefinition]):
    unique_key_columns = [cd for cd in cds if cd.column_single_unique]
    status_columns = [cd for cd in cds if cd.column_name.endswith("status")]
    if not unique_key_columns:
        logger.info(f"{table} of {schema} does not have unique key column")
    status_suffix = ''
    status_param_descr = ''
    method_descr_suffix = ''
    status_param_list = ''
    if status_columns:
        status_fields = [first_upper_case(sc.field_name) for sc in status_columns]
        status_comments = []
        status_suffix = f"And{'And'.join(status_fields)}"
        for status_column in status_columns:
            status_comments.append(short_comment)
            status_param_descr += ConstantUtil.JAVACLASS_METHOD_PARAM_DESCRIPTION_TEMPLATE.safe_substitute(
                NEW_LINE=ConstantUtil.NEW_LINE,
                param_name=status_column.field_name,
                param_type=f"{status_column.field_type} {status_column.column_comment}")
            status_param_list += f", @Param(\"{status_column.field_name}\") {status_column.field_type} {status_column.field_name}"
        method_descr_suffix = f", {', '.join(status_comments)}, {', '.join(status_comments)}作为可选条件"

    xml_mapper = ''
    java_mapper = ''
    for unique_key_column in unique_key_columns:
        method_name = f"findBy{first_upper_case(unique_key_column.field_name)}In{status_suffix}"
        unique_key_comment = f"{self.get_short_comment(unique_key_column.column_comment)}集合"
        method_description = f"通过[{unique_key_comment}" \
                             f"{method_descr_suffix}]查询数据"
        unique_key_collection_type = f"Collection<{unique_key_column.field_type}>"
        unique_key_collection_name = f"{unique_key_column.field_name}s"
        param_descr = ConstantUtil.JAVACLASS_METHOD_PARAM_DESCRIPTION_TEMPLATE.safe_substitute(
            NEW_LINE=ConstantUtil.NEW_LINE,
            param_name=unique_key_collection_name,
            param_type=f"{unique_key_collection_type} {unique_key_comment}") + status_param_descr
        param_list = f"@Param(\"{unique_key_collection_name}\") {unique_key_collection_type}" \
                     f" {unique_key_collection_name}{status_param_list}"
        java_mapper += ConstantUtil.JAVA_MAPPER_METHOD_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description=method_description,
                             param_description=param_descr,
                             return_type=f"List<{entity_name}>",
                             method_name=method_name,
                             param_list=param_list)
    return java_mapper, xml_mapper


def auto_generate_mapper(**kwargs):
    """ Automatically generate mappers corresponding to database tables """

    schema = kwargs.get('schema', '')
    table_name = kwargs.get('table_name', '')
    entity_name = kwargs.get('entity_name', '')
    table_description = kwargs.get('table_description', f'{table_name} mapper')
    file_save_dir = kwargs.get("file_save_dir", "")
    column_definitions = kwargs.get('column_definitions', [])
    author = kwargs.get('author', 'auto generate')
    logger.info(f'start to generate {table_name} of {schema} mybatis mapper')
    # repository name
    repository_name = f"{entity_name}Repository"
    repository_package = f'package com.hx.ylb.common.{schema}.repository;'
    entity_package = f'com.hx.ylb.common.entity.{schema}.{entity_name}'
    # repository default import
    repository_import_set = {entity_package,
                             'org.springframework.stereotype.Repository'}
    create_date = datetime.datetime.now().strftime(ConstantUtil.CREATE_DATE_FORMAT)
    class_description = ConstantUtil.JAVA_CLASS_DESCRIPTION_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                                                                     author=author,
                                                                                     description=table_description,
                                                                                     create_date=create_date)

    java_mapper_methods, unique_key_xml_method = get_find_by_unique_keys(schema,
                                                                         table_name,
                                                                         entity_name,
                                                                         column_definitions)
    if java_mapper_methods:
        repository_import_set.add("reactor.core.publisher.Flux")
        repository_import_set.add("reactor.core.publisher.Mono")
    java_mapper_file_name = f"{repository_name}.java"
    mapper_import = java_import_sort(repository_import_set)
    java_mapper = ConstantUtil.JAVA_MAPPER_CLASS_TEMPLATE \
        .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                         package=repository_package,
                         mapper_import=mapper_import,
                         class_description=class_description,
                         class_name=f"{repository_name} extends CrudRepository<{entity_name}>",
                         mapper_methods=java_mapper_methods)
    # generate java mapper
    write_file(java_mapper_file_name, java_mapper, file_save_dir)
    logger.info(f'successfully generate {table_name} of {schema} java mapper')

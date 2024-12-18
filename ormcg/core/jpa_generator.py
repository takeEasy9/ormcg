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
from ormcg.core.orm_java_generator import java_import_sort, get_default_methods
from ormcg.utils.constant_util import ConstantUtil
from ormcg.utils.enum_util import OrmCgEnum
from ormcg.utils.file_util import write_file

"""R2dbcRepository, CrudRepository"""


def auto_generate_repository(**kwargs):
    """ Automatically generate repository corresponding to database tables """

    schema = kwargs.get('schema', '')
    table_name = kwargs.get('table_name', '')
    entity_name = kwargs.get('entity_name', '')
    table_description = kwargs.get('table_description', f'{table_name} mapper')
    file_save_dir = kwargs.get("file_save_dir", "")
    column_definitions = kwargs.get('column_definitions', [])
    author = kwargs.get('author', 'auto generate')
    jpa_repository = kwargs.get('jpa_repository', 'crud')
    logger.info(f'start to generate {table_name} of {schema} jpa repository')
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
    java_mapper_methods, unique_key_xml_method = get_default_methods(schema,
                                                                     table_name,
                                                                     entity_name,
                                                                     column_definitions,
                                                                     ConstantUtil.MAPPER_PARAM_JPA_TEMPLATE,
                                                                     OrmCgEnum.ORM.ORM_JPA.get_value(),
                                                                     jpa_repository)
    if java_mapper_methods and jpa_repository == OrmCgEnum.JPARepository.R2DBC_REPOSITORY.get_value():
        repository_import_set.add("reactor.core.publisher.Flux")
        repository_import_set.add("reactor.core.publisher.Mono")
        repository_import_set.add("org.springframework.data.r2dbc.repository.R2dbcRepository")
        base_repository_short_name = 'R2dbcRepository'
    else:
        repository_import_set.add("org.springframework.data.repository.CrudRepository")
        base_repository_short_name = 'CrudRepository'
    java_mapper_file_name = f"{repository_name}.java"
    mapper_import = java_import_sort(repository_import_set)
    primary_column = [cd for cd in column_definitions if cd.column_single_unique and cd.column_key_type == 'PRI']
    assert primary_column, f'{schema}.{table_name} doesnt have primary key'
    primary_key_type = primary_column[0].field_type
    class_name = f'{repository_name} extends {base_repository_short_name}<{entity_name}, {primary_key_type}>'
    java_mapper = ConstantUtil.JAVA_MAPPER_CLASS_TEMPLATE \
        .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                         package=repository_package,
                         mapper_import=mapper_import,
                         class_description=class_description,
                         class_name=class_name,
                         mapper_methods=java_mapper_methods)
    # generate java mapper
    write_file(java_mapper_file_name, java_mapper, file_save_dir)
    logger.info(f'successfully generate {table_name} of {schema} java mapper')

# -*- coding: utf-8 -*-

"""
@author he.wei
@version 1.0.0
@since 1.0.0
@description base class
@createDate 2024/10/11 14:03
"""
import datetime

from ormcg.config.logger_config import logger
from ormcg.utils.constant_util import ConstantUtil, EntitySuperClass
from ormcg.utils.enum_util import OrmCgEnum
from ormcg.utils.file_util import write_file
from ormcg.utils.string_util import first_upper_case, to_camel_case


def get_entity_super_class(column_definitions):
    same_field_count = {}
    for c in column_definitions:
        for key, value in ConstantUtil.ENTITY_SUPER_CLASS_MAP.items():
            if c.field_name in value.fields:
                count = same_field_count.get(key, 0)
                count += 1
                same_field_count[key] = count
    if same_field_count:
        ordered_by_count_list = sorted(same_field_count.items(), key=lambda entry: entry[1], reverse=True)
        super_class1 = ordered_by_count_list[0]
        super_class2 = ordered_by_count_list[1]
        if super_class1[1] == super_class2[1] \
                and len(ConstantUtil.ENTITY_SUPER_CLASS_MAP.get(super_class1[0]).fields) \
                == len(ConstantUtil.ENTITY_SUPER_CLASS_MAP.get(super_class2[0]).fields):
            logger.error(f'there is more than one super class: {super_class1[0], super_class2[0]}')
        return ConstantUtil.ENTITY_SUPER_CLASS_MAP.get(super_class1[0])
    else:
        return EntitySuperClass('java.io.Serializable', 'Serializable', {}, "implements")


def build_to_string_method(column_position, field_type: str, name_left: str, name_right: str):
    if 'String' == field_type:
        enclose_left = '\''
        enclose_right = " + '\\'' "
    else:
        enclose_left = ''
        enclose_right = ''
    to_string_field = ConstantUtil.JAVA_TO_STRING_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                                                           field_name_left=name_left,
                                                                           field_name_right=name_right,
                                                                           enclose_left=enclose_left,
                                                                           enclose_right=enclose_right) \
                      + '                ' \
                      + ConstantUtil.NEW_LINE
    if column_position == 1:
        to_string_field = to_string_field.replace(', ', '', 1)
    return to_string_field


def java_import_sort(import_packages: set):
    if not import_packages:
        return ''
    # usual java package
    usual_packages = []
    # java builtin type
    java_builtin_packages = []
    for p in import_packages:
        p = f'import {p};'
        if p.find('java.') != -1:
            java_builtin_packages.append(p)
        else:
            usual_packages.append(p)
    res = ''
    if usual_packages:
        usual_packages.sort(key=lambda i: i[:8])
        res += ConstantUtil.NEW_LINE.join(usual_packages)
    if res:
        res += ConstantUtil.NEW_LINE * 2
    if java_builtin_packages:
        java_builtin_packages.sort(key=lambda i: i[:8])
        res += ConstantUtil.NEW_LINE.join(java_builtin_packages)
    return res


def auto_generate_java_entity(**kwargs):
    """ Automatically generate entity classes corresponding to database tables """
    schema = kwargs.get('schema', '')
    table_name = kwargs.get('table_name', '')
    entity_name = first_upper_case(to_camel_case(table_name))
    author = kwargs.get('author', 'auto generate')
    table_description = kwargs.get('table_description', f'{table_name} entity')
    file_save_dir = kwargs.get("file_save_dir", "")
    column_definitions = kwargs.get('column_definitions', [])
    orm = kwargs.get('orm', OrmCgEnum.ORM.ORM_MYBATIS.get_value())
    logger.info(f'start to generate to {table_name} of {schema} entity')
    if not column_definitions:
        logger.error(f'generate to {table_name} of {schema} entity, column_definitions is empty')
    entity_super_class = get_entity_super_class(column_definitions)
    create_date = datetime.datetime.now().strftime(ConstantUtil.CREATE_DATE_FORMAT)
    entity_import_set = set()
    entity_import_set.add(entity_super_class.package)
    class_description = ConstantUtil.JAVA_CLASS_DESCRIPTION_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                                                                     author=author,
                                                                                     description=table_description,
                                                                                     create_date=create_date)
    # entity field
    entity_fields = ''
    # getter setter method
    getter_setter_methods = ''
    # to_string method
    to_string = ''
    if entity_super_class.super_class != 'Serializable':
        to_string += build_to_string_method(1, 'super', 'super', 'super.toString()')

    class_annotations = ''
    if orm == OrmCgEnum.ORM.ORM_JPA.get_value():
        entity_import_set.add('javax.persistence.Entity')
        entity_import_set.add('org.springframework.data.relational.core.mapping.Table')
        class_annotations = '@Entity' + ConstantUtil.NEW_LINE \
                            + f'@Table(schema = "{schema}", name = "{table_name}")' \
                            + ConstantUtil.NEW_LINE

    for column in column_definitions:
        if column.field_name in entity_super_class.fields:
            continue
        if column.import_flag:
            entity_import_set.add(column.field_type_with_package)
        field_annotation = f'{ConstantUtil.NEW_LINE}    @Column("{column.field_name}")' \
            if orm == OrmCgEnum.ORM.ORM_JPA.get_value() else ''
        entity_field = ConstantUtil.JAVA_CLASS_FIELD_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                                                              comment=column.column_comment,
                                                                              field_annotation=field_annotation,
                                                                              field_type=column.field_type,
                                                                              field_name=column.field_name)
        entity_fields += entity_field
        # generate getter method
        getter_method = ConstantUtil.JAVA_CLASS_GETTER_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             field_type=column.field_type,
                             getter=column.field_getter,
                             field_name=column.field_name)
        getter_setter_methods += getter_method
        # generate setter method
        setter_method = ConstantUtil.JAVA_CLASS_SETTER_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             field_type=column.field_type,
                             setter=column.field_setter,
                             field_name=column.field_name)

        getter_setter_methods += setter_method
        to_string += build_to_string_method(column.column_order, column.field_type,
                                            column.field_name, column.field_name)

    to_string_method = ConstantUtil.JAVA_CLASS_TO_STRING_METHOD_TEMPLATE \
        .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                         class_name=entity_name,
                         to_string=to_string)
    entity_package = f'package com.hx.ylb.common.entity.{schema};'

    entity_imports = java_import_sort(entity_import_set)
    java_entity_class_content = ConstantUtil.JAVA_ENTITY_CLASS_TEMPLATE \
        .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                         package=entity_package,
                         entity_import=entity_imports,
                         class_description=class_description,
                         class_annotations=class_annotations,
                         class_name=entity_name,
                         inherit_word=entity_super_class.inherit_word,
                         super_class=entity_super_class.class_name,
                         entity_fields=entity_fields,
                         getter_setter_methods=getter_setter_methods,
                         to_string_method=to_string_method)
    file_name = entity_name + '.java'
    write_file(file_name, java_entity_class_content, file_save_dir)
    logger.info(f'successfully generate {table_name} of {schema} java entity')

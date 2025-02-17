# -*- coding: utf-8 -*-

"""
@author takeEasy9
@version 1.0.0
@since 1.0.0
@description base class
@createDate 2024/10/11 14:03
"""
import datetime
from string import Template

from sqlalchemy import and_

from ormcg.config.logger_config import logger
from ormcg.config.mysql_config import MysqlConfiguration
from ormcg.config.ormcg_config import OrmCgConfiguration
from ormcg.db.column_definition import ColumnDefinition
from ormcg.db.mysql.mysql_information_schema_models import MysqlStatisticsModel, MysqlTablesModel, MysqlColumnsModel
from ormcg.utils.constant_util import ConstantUtil, EntitySuperClass
from ormcg.utils.enum_util import OrmCgEnum
from ormcg.utils.file_util import write_file
from ormcg.utils.string_util import first_upper_case, to_camel_case


def mysql_to_column_definition(columns, index_name_columns_dict):
    column_definitions = []
    for column in columns:
        column_definition_dict = {}
        column_name = column.column_name.lower()
        column_definition_dict['column_name'] = column_name
        column_definition_dict['column_comment'] = column.column_comment
        column_data_type = column.data_type.upper()
        column_definition_dict['column_data_type'] = column_data_type
        column_definition_dict['column_key_type'] = column.column_key
        if column_definition_dict['column_name'] in index_name_columns_dict:
            # determine if the column is a single column unique index
            index_name = index_name_columns_dict[column_definition_dict['column_name']]
            column_name_set = index_name_columns_dict[index_name]
            column_definition_dict['column_single_unique'] = len(column_name_set) == 1
        field_name = to_camel_case(column_name)
        column_definition_dict['field_name'] = field_name
        if column_data_type in ConstantUtil.MYSQL_JAVA_MAP:
            java_type_info = ConstantUtil.MYSQL_JAVA_MAP.get(column_data_type)
            field_type = java_type_info.java_type
            import_flag = bool(java_type_info.import_flag)
            field_type_with_package = java_type_info.package
        else:
            logger.error(f'mysql data type:{column_data_type} cannot find its corresponding Java type')
            field_type = 'UnknownType ' + column_data_type
            import_flag = False
            field_type_with_package = None
        column_definition_dict['field_type'] = field_type
        column_definition_dict['import_flag'] = import_flag
        column_definition_dict['field_type_with_package'] = field_type_with_package
        field_getter = f'get{first_upper_case(field_name)}'
        column_definition_dict['field_getter'] = field_getter
        field_setter = f'set{first_upper_case(field_name)}'
        column_definition_dict['field_setter'] = field_setter
        jdbc_type = ConstantUtil.MYSQL_DATA_TYPE_JDBC_TYPE_MAP.get(column_data_type, 'unknown jdbcType')
        column_definition_dict['jdbc_type'] = jdbc_type
        column_definition_dict['column_order'] = column.ordinal_position
        column_definition_dict['char_max_length'] = column.character_maximum_length
        column_definition_dict['numeric_precision'] = column.numeric_precision
        column_definition_dict['numeric_scale'] = column.numeric_scale
        column_definition_dict['is_nullable'] = True if column.is_nullable == 'YES' else False
        column_definition = ColumnDefinition(**column_definition_dict)
        column_definitions.append(column_definition)

    # sort by column order
    column_definitions.sort(key=lambda c: c.column_order)
    return column_definitions


def auto_generate(**kwargs):
    env = kwargs.get('env', "dev")
    schema_name = kwargs.get('schema', None)
    table_name = kwargs.get('table_name', None)
    orm_generator = kwargs.get('orm_generator',  None)
    try:
        logger.info(f'start to load ormcg config file, env: {env}')
        orm_configuration = OrmCgConfiguration(env, schema_name)
        logger.info('ormcg config file is loaded completely')
        mysql_configuration = MysqlConfiguration(orm_configuration)
        kwargs['mysql_configuration'] = mysql_configuration
        logger.info(f'Start to check {table_name} of {schema_name} exists')
        # check if the table exists
        with mysql_configuration.session_factory() as session:
            table = session.query(MysqlTablesModel) \
                .filter(and_(MysqlTablesModel.table_schema == schema_name,
                             MysqlTablesModel.table_name == table_name)) \
                .first()
            if not table:
                logger.error(f'{table_name} of {schema_name} dose not exist, '
                             f'please check your [env, schema, table_name] args')
                return
            columns = session.query(MysqlColumnsModel) \
                .filter(and_(MysqlColumnsModel.table_schema == schema_name,
                             MysqlColumnsModel.table_name == table_name)) \
                .order_by(MysqlColumnsModel.ordinal_position.asc()) \
                .all()
            if not columns:
                logger.error(f'column of {table_name} dose not exist,, unable to generate mybatis code')
                return
            index_infos = session.query(MysqlStatisticsModel) \
                .filter(and_(MysqlStatisticsModel.table_schema == schema_name,
                             MysqlStatisticsModel.table_name == table_name)) \
                .all()
            index_name_columns_dict = {}
            for index in index_infos:
                column_name = index.column_name.lower()
                if index.index_name in index_name_columns_dict:
                    index_name_columns_dict.get(index.index_name).add(column_name)
                else:
                    column_name_set = {column_name}
                    index_name_columns_dict[index.index_name] = column_name_set
                index_name_columns_dict[column_name] = index.index_name
            column_definitions = mysql_to_column_definition(columns, index_name_columns_dict)
            kwargs['column_definitions'] = column_definitions
            kwargs['entity_name'] = first_upper_case(to_camel_case(table_name))
            kwargs['java_version'] = orm_configuration.orm_java_version
            kwargs['entity_super_classes'] = orm_configuration.entity_super_classes
            if OrmCgEnum.ORM.ORM_JPA.get_value() == kwargs.get('orm', None):
                kwargs['entity_package'] = orm_configuration.orm_jpa_entity_package
                kwargs['entity_path'] = orm_configuration.orm_jpa_entity_path
                kwargs['repository_package'] = orm_configuration.orm_jpa_repository_package
                kwargs['repository_path'] = orm_configuration.orm_jpa_repository_path
            else:
                kwargs['entity_package'] = orm_configuration.orm_mybatis_entity_package
                kwargs['entity_path'] = orm_configuration.orm_mybatis_entity_path
                kwargs['mapper_package'] = orm_configuration.orm_mybatis_mapper_package
                kwargs['mapper_path'] = orm_configuration.orm_mybatis_mapper_path
                kwargs['dao_package'] = orm_configuration.orm_mybatis_mapper_package
                kwargs['dao_path'] = orm_configuration.orm_mybatis_mapper_path
            # generate entity
            auto_generate_java_entity(**kwargs)
            orm_generator(**kwargs)
    except Exception as e:
        logger.error(f'mysql：{table_name} of {schema_name} mybatis template code generation has failed,'
                     f' error is：{e}')


def get_entity_super_class(column_definitions, entity_super_classes):
    same_field_count = {}
    for index, entity_super_class in enumerate(entity_super_classes):
        # 计算匹配的字段数量
        match_count = sum(1 for col in column_definitions if col.field_name in entity_super_class['fields'])
        same_field_count[index] = match_count
    if same_field_count:
        # 按匹配数量降序排序
        ordered_by_count_list = sorted(same_field_count.items(), key=lambda entry: entry[1], reverse=True)
        super_class_entity = entity_super_classes[ordered_by_count_list[0][0]]
        return super_class_entity
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
    entity_name = kwargs.get('entity_name', '')
    entity_package = kwargs.get('entity_package', '')
    author = kwargs.get('author', 'auto generate')
    table_description = kwargs.get('table_description', f'{table_name} entity')
    entity_path = kwargs.get("entity_path", '')
    column_definitions = kwargs.get('column_definitions', [])
    orm = kwargs.get('orm', OrmCgEnum.ORM.ORM_MYBATIS.get_value())
    logger.info(f'start to generate to {table_name} of {schema} entity')
    if not column_definitions:
        logger.error(f'generate to {table_name} of {schema} entity, column_definitions is empty')
    entity_super_classes = kwargs.get('entity_super_classes', [])
    entity_super_class = get_entity_super_class(column_definitions, entity_super_classes)
    create_date = datetime.datetime.now().strftime(ConstantUtil.CREATE_DATE_FORMAT)
    entity_import_set = set()
    entity_import_set.add(f'{entity_super_class["entity_package"]}.{entity_super_class["entity_name"]}')
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
    if entity_super_class['entity_name'] != 'Serializable':
        to_string += build_to_string_method(1, 'super', 'super', 'super.toString()')

    class_annotations = ''
    java_version = kwargs.get('java_version', 11)
    jpa_annotation_package_prefix = 'jakarta' if java_version >= 9 else 'javax'
    if orm == OrmCgEnum.ORM.ORM_JPA.get_value():
        class_annotations = f'@Entity{ConstantUtil.NEW_LINE}@Table(schema ="{schema}", name = "{table_name}"){ConstantUtil.NEW_LINE} '
        entity_import_set.add(f'{jpa_annotation_package_prefix}.persistence.Entity')
        entity_import_set.add(f'{jpa_annotation_package_prefix}.persistence.Table')
        entity_import_set.add(f'{jpa_annotation_package_prefix}.persistence.Column')

    field_annotation = ''
    for column in column_definitions:
        if column.field_name in entity_super_class['fields']:
            continue
        if column.import_flag:
            entity_import_set.add(column.field_type_with_package)
        if orm == OrmCgEnum.ORM.ORM_JPA.get_value():
            annotation_content = f'name = "{column.column_name}"'
            if column.column_key_type != 'PRI' and column.column_single_unique:
                annotation_content += ', unique=true'
            if column.is_nullable:
                annotation_content += ', nullable=true'
            field_annotation = f'{ConstantUtil.NEW_LINE}    @Column({annotation_content})'

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

    entity_imports = java_import_sort(entity_import_set)
    java_entity_class_content = ConstantUtil.JAVA_ENTITY_CLASS_TEMPLATE \
        .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                         package=entity_package,
                         entity_import=entity_imports,
                         class_description=class_description,
                         class_annotations=class_annotations,
                         class_name=entity_name,
                         inherit_word=entity_super_class['inherit_word'],
                         super_class=entity_super_class['entity_name'],
                         entity_fields=entity_fields,
                         getter_setter_methods=getter_setter_methods,
                         to_string_method=to_string_method)
    file_name = entity_name + '.java'
    write_file(file_name, java_entity_class_content, entity_path)
    logger.info(f'successfully generate {table_name} of {schema} java entity')


def get_short_comment(column_comment):
    en_comma_end = column_comment.find(',')
    cn_comma_end = column_comment.find('，')
    if en_comma_end != -1:
        return column_comment[:en_comma_end]
    elif cn_comma_end != -1:
        return column_comment[:cn_comma_end]
    else:
        return column_comment


def get_non_null_and(field_name, field_type):
    if field_type in ConstantUtil.NON_NULL_AND_STRING_SET:
        return ConstantUtil.NON_NULL_AND_STRING_TEMPLATE \
            .safe_substitute(property_name=field_name)
    elif field_type in ConstantUtil.PROPERTY_VALID_AND_NUMERICAL_SET:
        return ConstantUtil.NON_NULL_AND_NUMERICAL_TEMPLATE \
            .safe_substitute(property_name=field_name)
    elif field_type in ConstantUtil.NON_NULL_VALID_AND_OTHER_SET:
        return ''


def get_default_methods(schema, table, entity_name, cds: list[ColumnDefinition],
                        param_template: Template,
                        orm_type: str = OrmCgEnum.ORM.ORM_MYBATIS.get_value(),
                        interface_type: str = OrmCgEnum.JPARepository.CRUD_REPOSITORY.get_value()):
    unique_key_columns = [cd for cd in cds if cd.column_single_unique]
    status_columns = [cd for cd in cds if cd.column_name.endswith("status")]
    if not unique_key_columns:
        logger.info(f"{table} of {schema} does not have unique key column")
    if_status = ''
    status_suffix = ''
    status_param_descr = ''
    method_descr_suffix = ''
    status_param_list = ''
    method_descr_option_tip_suffix = ''
    multi_return_type = 'List'
    return_type_prefix = ''
    return_type_suffix = ''
    if orm_type == OrmCgEnum.ORM.ORM_MYBATIS.get_value():
        method_descr_option_tip_suffix = '作为可选条件'
    elif orm_type == OrmCgEnum.ORM.ORM_JPA.get_value():
        method_descr_option_tip_suffix = '作为查询条件'
        if interface_type == OrmCgEnum.JPARepository.R2DBC_REPOSITORY.get_value():
            multi_return_type = 'Flux'
            return_type_prefix = 'Mono<'
            return_type_suffix = '>'
    if status_columns:
        status_fields = [first_upper_case(sc.field_name) for sc in status_columns]
        status_comments = []
        status_suffix = f"And{'And'.join(status_fields)}"
        for status_column in status_columns:
            non_null_and = get_non_null_and(status_column.field_name,
                                            status_column.field_type)
            if_status += ConstantUtil.MAPPER_XML_DYNAMICAL_UPDATE_IF_TEMPLATE \
                .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                 property_name=status_column.field_name,
                                 pre_handler='',
                                 non_null_and=non_null_and,
                                 prefix='AND ',
                                 column_name=status_column.column_name,
                                 operator='=',
                                 suffix='')
            short_comment = get_short_comment(status_column.column_comment)
            status_comments.append(short_comment)
            status_param_descr += ConstantUtil.JAVACLASS_METHOD_PARAM_DESCRIPTION_TEMPLATE.safe_substitute(
                NEW_LINE=ConstantUtil.NEW_LINE,
                param_name=status_column.field_name,
                param_type=f"{status_column.field_type} {status_column.column_comment}")
            status_param_list += ', ' + param_template.safe_substitute(param_name=status_column.field_name,
                                                                  param_type=status_column.field_type)
        method_descr_suffix = f", {', '.join(status_comments)}, {', '.join(status_comments)}{method_descr_option_tip_suffix}"
    xml_mapper = ''
    java_mapper = ''
    for unique_key_column in unique_key_columns:
        # single return value method
        dynamical_where = ''
        dynamical_where += ConstantUtil.MAPPER_XML_SELECT_FIND_BY_UNIQUE_KEY_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             column_name=unique_key_column.column_name,
                             field_name=unique_key_column.field_name, )
        dynamical_where += if_status
        method_name = f"findBy{first_upper_case(unique_key_column.field_name)}{status_suffix}"
        unique_key_comment = f"{get_short_comment(unique_key_column.column_comment)}"
        method_description = f"通过[{unique_key_comment}" \
                             f"{method_descr_suffix}]查询数据"
        xml_mapper += ConstantUtil.MAPPER_XML_SELECT_BY_DYNAMICAL_CONDITION_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description=method_description,
                             method_name=method_name,
                             db=schema,
                             table=table,
                             dynamical_condition=dynamical_where)
        param_descr = ConstantUtil.JAVACLASS_METHOD_PARAM_DESCRIPTION_TEMPLATE.safe_substitute(
            NEW_LINE=ConstantUtil.NEW_LINE,
            param_name=unique_key_column.field_name,
            param_type=f"{unique_key_column.field_type} {unique_key_comment}") + status_param_descr
        param_list = param_template.substitute(param_name=unique_key_column.field_name,
                                               param_type=unique_key_column.field_type) + status_param_list
        java_mapper += ConstantUtil.JAVA_MAPPER_METHOD_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description=method_description,
                             param_description=param_descr,
                             return_type=f"{return_type_prefix}{entity_name}{return_type_suffix}",
                             method_name=method_name,
                             param_list=param_list)
        # multiple return value method
        dynamical_where = ''
        dynamical_where += ConstantUtil.MAPPER_XML_SELECT_FIND_BY_FOREACH_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             key_collection=f"{unique_key_column.field_name}s",
                             column_name=unique_key_column.column_name,
                             key_name=unique_key_column.field_name, )
        dynamical_where += if_status
        method_name = f"findBy{first_upper_case(unique_key_column.field_name)}In{status_suffix}"
        unique_key_comment = f"{get_short_comment(unique_key_column.column_comment)}集合"
        method_description = f"通过[{unique_key_comment}" \
                             f"{method_descr_suffix}]查询数据"
        xml_mapper += ConstantUtil.MAPPER_XML_SELECT_BY_DYNAMICAL_CONDITION_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description=method_description,
                             method_name=method_name,
                             db=schema,
                             table=table,
                             dynamical_condition=dynamical_where)
        unique_key_collection_type = f"Collection<{unique_key_column.field_type}>"
        unique_key_collection_name = f"{unique_key_column.field_name}s"
        param_descr = ConstantUtil.JAVACLASS_METHOD_PARAM_DESCRIPTION_TEMPLATE.safe_substitute(
            NEW_LINE=ConstantUtil.NEW_LINE,
            param_name=unique_key_collection_name,
            param_type=f"{unique_key_collection_type} {unique_key_comment}") + status_param_descr
        param_list = param_template.substitute(param_name=unique_key_collection_name,
                                               param_type=unique_key_collection_type) + status_param_list
        java_mapper += ConstantUtil.JAVA_MAPPER_METHOD_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description=method_description,
                             param_description=param_descr,
                             return_type=f"{multi_return_type}<{entity_name}>",
                             method_name=method_name,
                             param_list=param_list)
    return java_mapper, xml_mapper

# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description:
@version: 1.0.0
@since: 2024/4/30 19:59
"""
import datetime
import string

from jinja2 import Environment, FileSystemLoader

from ormcg.config.logger_config import logger
from ormcg.core.orm_java_generator import get_default_methods
from ormcg.db.column_definition import ColumnDefinition
from ormcg.utils.constant_util import ConstantUtil, EntitySuperClass
from ormcg.utils.enum_util import OrmCgEnum
from ormcg.utils.file_util import write_file
from ormcg.utils.string_util import first_upper_case, first_lower_case, substr


class MyBatisGenerator:

    @staticmethod
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

    @staticmethod
    def classify_sort_java_import(import_packages: set):
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

    @staticmethod
    def to_string_per_field(column_position, field_type: string, name_left: string, name_right: string):
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

    @staticmethod
    def get_non_null_and(field_name, field_type):
        if field_type in ConstantUtil.NON_NULL_AND_STRING_SET:
            return ConstantUtil.NON_NULL_AND_STRING_TEMPLATE \
                .safe_substitute(property_name=field_name)
        elif field_type in ConstantUtil.PROPERTY_VALID_AND_NUMERICAL_SET:
            return ConstantUtil.NON_NULL_AND_NUMERICAL_TEMPLATE \
                .safe_substitute(property_name=field_name)
        elif field_type in ConstantUtil.NON_NULL_VALID_AND_OTHER_SET:
            return ''

    @staticmethod
    def mapper_xml_header(entity_package, column_definitions):
        """generate mybatis mapper xml file header, resultMap, Base_Column_List"""
        logger.info("start to generate mybatis mapper xml file header, resultMap, Base_Column_List")
        mapping = ''
        column_list = ''
        for column in column_definitions:
            result_type = 'id' if column.column_key_type == "PRI" else 'result'
            mapping += ConstantUtil.JAVA_MAPPER_XML_RESULT_MAPPING_TEMPLATE.safe_substitute(
                NEW_LINE=ConstantUtil.NEW_LINE,
                result_type=result_type,
                column=column.column_name,
                property=column.field_name,
                jdbcType=column.jdbc_type)
            column_list += ConstantUtil.JAVA_MAPPER_BASE_COLUMN_TEMPLATE.safe_substitute(
                NEW_LINE=ConstantUtil.NEW_LINE,
                column=column.column_name)
        # remove comma
        column_list = column_list[:-1]
        base_column_list = ConstantUtil.JAVA_MAPPER_BASE_COLUMN_LIST_TEMPLATE.safe_substitute(
            NEW_LINE=ConstantUtil.NEW_LINE,
            columns=column_list)
        result_map = ConstantUtil.JAVA_MAPPER_XML_RESULT_MAP_TEMPLATE.safe_substitute(
            NEW_LINE=ConstantUtil.NEW_LINE,
            entity_package=entity_package,
            mapping=mapping)
        return result_map, base_column_list

    def get_insert_columns_fields(cdf: ColumnDefinition, field_prefix: str, suffix: str):
        field_name = f'{field_prefix}{cdf.field_name}'
        non_null_and = MyBatisGenerator.get_non_null_and(field_name, cdf.field_type)
        column = ConstantUtil.MAPPER_XML_INSERT_IF_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             property_name=field_name,
                             non_null_and=non_null_and,
                             prefix='',
                             column_or_property_name=cdf.column_name,
                             suffix=suffix)
        field = ConstantUtil.MAPPER_XML_INSERT_IF_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             property_name=field_name,
                             non_null_and=non_null_and,
                             prefix='#{',
                             column_or_property_name=field_name,
                             suffix='}' + suffix)
        return column, field

    def get_save_dynamically_method(self, schema, table, cds: list[ColumnDefinition]):
        columns = ''
        fields = ''
        length = len(cds)
        last_index = length - 1
        for i in range(length):
            suffix = '' if last_index == i else ','
            c, f = MyBatisGenerator.get_insert_columns_fields(cds[i], '', suffix)
            columns += c
            fields += f
        return ConstantUtil.MAPPER_XML_INSERT_DYNAMICAL_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='动态地新增记录, 实体类对象字段不设值则插入时对应列不插入',
                             method_name='saveDynamically',
                             db=schema,
                             table=table,
                             column_list=columns,
                             property_list=fields)

    @staticmethod
    def get_save_usually_method(schema, table, cds: list[ColumnDefinition]):
        logger.info("start to generate  saveUsually  xml method")
        columns = ''
        fields = ''
        for column in cds:
            columns += ConstantUtil.MAPPER_XML_INSERT_USUAL_COLUMN_TEMPLATE \
                .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE, column=column.column_name)
            fields += ConstantUtil.MAPPER_XML_INSERT_USUAL_PROPERTY_TEMPLATE \
                .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                 prefix='',
                                 property_name=column.field_name)
        columns = columns[:-1]
        fields = fields[:-1]
        return ConstantUtil.MAPPER_XML_INSERT_USUAL_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='普通地新增记录, 默认全部字段插入',
                             method_name='saveUsually',
                             db=schema,
                             table=table,
                             column_list=columns,
                             property_list=fields)

    @staticmethod
    def get_save_all_method(schema, table, cds: list[ColumnDefinition]):
        logger.info("start to generate saveAll method xml")
        save_all_columns = ''
        save_all_fields = ''
        for column in cds:
            save_all_columns += ConstantUtil.MAPPER_XML_INSERT_USUAL_COLUMN_TEMPLATE \
                .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE, column=column.column_name)
            save_all_fields += ConstantUtil.MAPPER_XML_INSERT_USUAL_PROPERTY_TEMPLATE \
                .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                 prefix=ConstantUtil.DEFAULT_PROP_PREFIX,
                                 property_name=column.field_name)
        save_all_columns = save_all_columns[:-1]
        save_all_fields = save_all_fields[:-1]
        return ConstantUtil.MAPPER_XML_INSERT_BATCH_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description="批量新增记录",
                             method_name="saveAll",
                             db=schema,
                             table=table,
                             column_list=save_all_columns,
                             param_name="entities",
                             property_list=save_all_fields)

    @staticmethod
    def get_save_all_dynamically_method(schema, table, cds: list[ColumnDefinition]):
        logger.info("start to generate saveAll dynamically method xml")
        columns = ''
        fields = ''
        length = len(cds)
        last_index = length - 1
        for i in range(length):
            suffix = '' if last_index == i else ','
            c, f = MyBatisGenerator.get_insert_columns_fields(cds[i], ConstantUtil.DEFAULT_PROP_PREFIX, suffix)
            columns += c
            fields += f
        return ConstantUtil.MAPPER_XML_INSERT_BATCH_DYNAMICALLY_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='动态地批量新增记录'
                                                '使用该方法需将AllowMultiQueries参数, 设置为true, 为避免SQL阻塞, 使用该方法需限制单次批量更新数据数量',
                             method_name="saveAllDynamically",
                             db=schema,
                             table=table,
                             column_list=columns,
                             param_name="entities",
                             property_list=fields)

    @staticmethod
    def get_update_dynamically_column_prop_list(cds: list[ColumnDefinition],
                                                version_control_column: str,
                                                batch: bool) -> tuple[str, str]:
        column_property_list = ''
        extra_criteria = ''
        length = len(cds)
        last_index = length - 1
        if batch:
            comment = ''
            prop_prefix = ConstantUtil.DEFAULT_PROP_PREFIX
        else:
            comment = f'            <!-- 版本编码,用于控制并发 -->{ConstantUtil.NEW_LINE}'
            prop_prefix = ''
        for i in range(length):
            column = cds[i]
            suffix = '' if i == last_index else ','
            if column.column_name == version_control_column:
                extra_criteria = f'AND {column.column_name} = ' + '#{' + f'{prop_prefix}{column.field_name}' + '}'
                column_property_list += ConstantUtil.MAPPER_XML_USUAL_UPDATE_TEMPLATE \
                    .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                     comment=comment,
                                     pre_handler='',
                                     property_name=f'{prop_prefix}{column.field_name}',
                                     column_name=column.column_name,
                                     operator='=',
                                     prefix='',
                                     suffix=f' + 1{suffix}')
            else:
                field_name = f'{prop_prefix}{column.field_name}'
                non_null_and = MyBatisGenerator.get_non_null_and(field_name, column.field_type)
                column_property_list += ConstantUtil.MAPPER_XML_DYNAMICAL_UPDATE_IF_TEMPLATE \
                    .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                     property_name=field_name,
                                     non_null_and=non_null_and,
                                     pre_handler='',
                                     prefix='',
                                     column_name=column.column_name,
                                     operator='=',
                                     suffix=suffix)
        return column_property_list, extra_criteria

    @staticmethod
    def get_update_by_id_dynamically_method(schema, table, cds: list[ColumnDefinition],
                                            version_control_column: str) -> str:
        logger.info("start to generate dynamically update by id  xml method")
        column_property_list, extra_criteria = MyBatisGenerator \
            .get_update_dynamically_column_prop_list(cds, version_control_column, False)
        criteria_comment = f'{ConstantUtil.NEW_LINE}        <!-- 版本编码,用于控制并发 -->' \
            if extra_criteria else ''
        return ConstantUtil.MAPPER_XML_UPDATE_DYNAMICAL_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='动态地更新记录, 实体类对象字段不设值则更新时对应列不更新',
                             method_name="updateByIdDynamically",
                             db=schema,
                             table=table,
                             column_property_list=column_property_list,
                             criteria_comment=criteria_comment,
                             extra_criteria=extra_criteria)

    @staticmethod
    def get_update_usually_column_prop_list(cds: list[ColumnDefinition],
                                            version_control_column: str,
                                            batch: bool) -> tuple[str, str]:
        column_property_list = ''
        extra_criteria = ''
        length = len(cds)
        last_index = length - 1
        if batch:
            comment = ''
            prop_prefix = ConstantUtil.DEFAULT_PROP_PREFIX
        else:
            comment = f'            <!-- 版本编码,用于控制并发 -->{ConstantUtil.NEW_LINE}'
            prop_prefix = ''
        for i in range(length):
            column = cds[i]
            suffix = '' if i == last_index else ','
            if column.column_name == version_control_column:
                extra_criteria = f'AND {column.column_name} = ' + '#{' + f'{prop_prefix}{column.field_name}' + '}'
                column_property_list += ConstantUtil.MAPPER_XML_USUAL_UPDATE_TEMPLATE \
                    .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                     comment=comment,
                                     pre_handler='',
                                     property_name=column.field_name,
                                     column_name=column.column_name,
                                     operator='=',
                                     prefix=prop_prefix,
                                     suffix=f' + 1{suffix}')
            else:
                column_property_list += ConstantUtil.MAPPER_XML_USUAL_UPDATE_TEMPLATE \
                    .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                     comment='',
                                     pre_handler='',
                                     property_name=column.field_name,
                                     column_name=column.column_name,
                                     operator='=',
                                     prefix=prop_prefix,
                                     suffix=suffix)
        return column_property_list, extra_criteria

    @staticmethod
    def get_update_by_id_usually_method(schema, table, cds: list[ColumnDefinition],
                                        version_control_column: str) -> str:
        logger.info("start to generate usually update by id  xml method")
        column_property_list, extra_criteria = MyBatisGenerator \
            .get_update_usually_column_prop_list(cds, version_control_column, False)
        criteria_comment = f'{ConstantUtil.NEW_LINE}        <!-- 版本编码,用于控制并发 -->' if extra_criteria else ''
        return ConstantUtil.MAPPER_XML_UPDATE_USUAL_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='普通地更新记录, 实体类对象字段值即为更新时对应列的值',
                             method_name='updateByIdUsually',
                             db=schema,
                             table=table,
                             column_property_list=column_property_list,
                             criteria_comment=criteria_comment,
                             extra_criteria=extra_criteria)

    @staticmethod
    def get_update_all_dynamically_method(schema, table, cds: list[ColumnDefinition], version_control_column: str):
        logger.info("start to generate dynamically update by id  xml method")
        column_property_list, extra_criteria = MyBatisGenerator \
            .get_update_dynamically_column_prop_list(cds, version_control_column, True)
        return ConstantUtil.MAPPER_XML_UPDATE_BATCH_DYNAMICALLY_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='动态地批量更新记录, 实体类对象字段值即为更新时对应列的值,'
                                                '使用该方法需将AllowMultiQueries参数, 设置为true, 为避免SQL阻塞, 使用该方法需限制单次批量更新数据数量',
                             method_name='updateAllByIdDynamically',
                             param_name='entities',
                             db=schema,
                             table=table,
                             column_property_list=column_property_list,
                             extra_criteria=extra_criteria)

    @staticmethod
    def get_update_all_usually_method(schema, table, cds: list[ColumnDefinition], version_control_column: str):
        logger.info("start to generate usually update by id  xml method")
        column_property_list, extra_criteria = MyBatisGenerator \
            .get_update_usually_column_prop_list(cds, version_control_column, True)
        return ConstantUtil.MAPPER_XML_UPDATE_BATCH_USUALLY_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='普通地批量更新记录, 实体类对象字段值即为更新时对应列的值,'
                                                ' 使用该方法需将AllowMultiQueries参数, 设置为true, 为避免SQL阻塞, 使用该方法需限制单次批量更新数据数量',
                             method_name='updateAllByIdUsually',
                             param_name='entities',
                             db=schema,
                             table=table,
                             column_property_list=column_property_list,
                             extra_criteria=extra_criteria)

    def get_find_all_method(self, schema, table, cds: list[ColumnDefinition]):
        # 过滤
        def is_where_column(cd):
            if cd.column_key_type in {'PRI', 'UNIQUE', 'Key'}:
                return True
            if cd.column_data_type not in ConstantUtil.MYSQL_JAVA_MAP:
                return False
            java_type = ConstantUtil.MYSQL_JAVA_MAP.get(cd.column_data_type).java_type
            if java_type == 'String' and cd.char_max_length <= ConstantUtil.QUERY_CONDITION_CHAR_MAX_LENGTH:
                return True
            if java_type == 'Boolean' or java_type == 'Long' or java_type == 'Integer':
                return True
            return False

        find_all_columns = [e for e in cds if is_where_column(e)]
        first_non_null_and = self.get_non_null_and(find_all_columns[0].field_name,
                                                   find_all_columns[0].field_type)
        dynamical_where = ConstantUtil.MAPPER_XML_DYNAMICAL_UPDATE_IF_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             property_name=find_all_columns[0].field_name,
                             non_null_and=first_non_null_and,
                             pre_handler='',
                             prefix='',
                             column_name=find_all_columns[0].column_name,
                             operator='=',
                             suffix='', )
        for i in range(1, len(find_all_columns)):
            column = find_all_columns[i]
            non_null_and = self.get_non_null_and(column.field_name, column.field_type)
            dynamical_where += ConstantUtil.MAPPER_XML_DYNAMICAL_UPDATE_IF_TEMPLATE \
                .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                 property_name=column.field_name,
                                 non_null_and=non_null_and,
                                 pre_handler='',
                                 prefix='AND ',
                                 column_name=column.column_name,
                                 operator='=',
                                 suffix='', )

        find_all_method = ConstantUtil.MAPPER_XML_SELECT_BY_DYNAMICAL_CONDITION_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='动态地查询记录, 实体类对象字段不设值则对应列不作为查询条件',
                             method_name="findAll",
                             db=schema,
                             table=table,
                             dynamical_condition=dynamical_where)
        find_one_method = ConstantUtil.MAPPER_XML_SELECT_BY_DYNAMICAL_CONDITION_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             method_description='动态地查询唯一一条记录, 实体类对象字段不设值则对应列不作为查询条件',
                             method_name="findOne",
                             db=schema,
                             table=table,
                             dynamical_condition=dynamical_where)
        return find_all_method + find_one_method

    def get_xml_mapper_crud_method(self, **kwargs):
        schema = kwargs.get("schema", "")
        table = kwargs.get("table", "")
        mapper_namespace = kwargs.get("mapper_namespace", "")
        column_definitions = kwargs.get("column_definitions", [])
        logger.info(f'{mapper_namespace} corresponding to xml file')
        mysql_configuration = kwargs.get("mysql_configuration", None)
        insert_columns = []
        update_columns = []
        select_where_columns = []
        for c in column_definitions:
            if c.column_name not in mysql_configuration.insert_exclude_columns:
                insert_columns.append(c)
            if c.column_name not in mysql_configuration.update_exclude_columns:
                update_columns.append(c)
            if c.column_name not in mysql_configuration.select_where_exclude_columns:
                select_where_columns.append(c)
        xml_mapper_crud_method = ''
        xml_mapper_crud_method += self.get_save_dynamically_method(schema, table, insert_columns)
        xml_mapper_crud_method += self.get_save_usually_method(schema, table, insert_columns)
        xml_mapper_crud_method += self.get_save_all_method(schema, table, insert_columns)
        xml_mapper_crud_method += self.get_save_all_dynamically_method(schema, table, insert_columns)
        xml_mapper_crud_method += self.get_update_by_id_dynamically_method(schema, table,
                                                                           update_columns,
                                                                           mysql_configuration.version_control_column)
        xml_mapper_crud_method += self.get_update_by_id_usually_method(schema, table,
                                                                       update_columns,
                                                                       mysql_configuration.version_control_column)
        xml_mapper_crud_method += self.get_update_all_dynamically_method(schema, table,
                                                                         update_columns,
                                                                         mysql_configuration.version_control_column)
        xml_mapper_crud_method += self.get_update_all_usually_method(schema, table,
                                                                     update_columns,
                                                                     mysql_configuration.version_control_column)
        xml_mapper_crud_method += self.get_find_all_method(schema, table, select_where_columns)
        return xml_mapper_crud_method

    def auto_generate_dao(self, schema,
                          entity_name,
                          table_name,
                          author,
                          table_description,
                          column_definitions,
                          file_save_dir):
        """Automatically generate DAO"""
        try:
            logger.info(f'start to generate {table_name} of {schema} DAO')
            jinja2_env = Environment(loader=FileSystemLoader('templates'))
            entity_name_first_lower = first_lower_case(entity_name)
            entity_package = f'com.hx.ylb.common.entity.{schema}.{entity_name}'
            mapper_package = f'com.hx.ylb.common.repository.{schema}.mapper.{entity_name}Mapper'
            # dao default import
            dao_import_set = {entity_package,
                              mapper_package,
                              'com.hx.ylb.common.util.CollectionUtil',
                              'com.hx.ylb.common.repository.CrudRepository',
                              'org.slf4j.Logger',
                              'org.slf4j.LoggerFactory',
                              'org.springframework.lang.NonNull',
                              'org.springframework.lang.Nullable',
                              'org.springframework.stereotype.Repository',
                              'java.util.List',
                              'java.util.Collection',
                              'java.util.Optional'}
            # unique index columns
            single_unique_columns = [c for c in column_definitions if c.column_single_unique]
            unique_key_query_methods = ''
            if single_unique_columns:
                dao_import_set.add('java.util.concurrent.CompletableFuture')
                dao_import_set.add('java.util.function.Function')
                dao_import_set.add('java.util.stream.Collectors')
                dao_import_set.add('java.util.Map')
                dao_import_set.add('java.util.HashMap')
                dao_import_set.add('org.springframework.scheduling.annotation.Async')
                # logically delete column
                status_columns = [cd for cd in column_definitions if cd.column_name.endswith("status")]
                status_column_params = ''
                status_params = ''
                status_fields = ''
                status_column_comments = ''
                status_column_comments_log = ''
                if status_columns:
                    status_column_params = ConstantUtil.NEW_LINE.join(
                        [f'* @param {sc.field_name} {sc.field_type} {sc.column_comment} '
                         for sc in status_columns])
                    status_params = f', {", ".join(["@Nullable " + sc.field_type + " " + sc.field_name for sc in status_columns])}'
                    status_fields = f', {", ".join([sc.field_name for sc in status_columns])}'
                    comments_join = ', '.join([substr(sc.column_comment, ',', '，') for sc in status_columns])
                    status_column_comments = f", {comments_join}, {comments_join}作为可选条件"
                    status_place_holders = ['{}'] * len(status_columns)
                    status_column_comments_log = f", {comments_join} <{'-'.join(status_place_holders)}>, {comments_join}作为可选条件"

                unique_key_entity_methods = []

                # unique Index Query Method Template
                unique_key_entity_method_template = jinja2_env.get_template("unique_key_method.template")
                for cd in single_unique_columns:
                    and_status = "And".join([first_upper_case(sc.field_name) for sc in status_columns])
                    query_by_unique_keys_method = f'queryBy{first_upper_case(cd.field_name)}InAnd{and_status}'
                    find_by_unique_keys_method = f'findBy{first_upper_case(cd.field_name)}InAnd{and_status}'
                    method = unique_key_entity_method_template.render(
                        unique_column_comment=substr(cd.column_comment, ',', '，'),
                        table_description=table_description,
                        field_name=cd.field_name,
                        unique_column_java_type=cd.field_type,
                        entity_name=entity_name,
                        entity_name_first_lower=entity_name_first_lower,
                        unique_key_field_getter=cd.field_getter,
                        status_column_params=status_column_params,
                        status_column_comments=status_column_comments,
                        status_params=status_params,
                        status_fields=status_fields,
                        query_by_unique_keys_method=query_by_unique_keys_method,
                        find_by_unique_keys_method=find_by_unique_keys_method,
                        status_column_comments_log=status_column_comments_log)
                    unique_key_entity_methods.append(method)

                method_sep = ConstantUtil.NEW_LINE * 2
                unique_key_query_methods = f"{ConstantUtil.NEW_LINE}{method_sep.join(unique_key_entity_methods)}"
            dao_import = self.classify_sort_java_import(dao_import_set)
            # 文件创建时间
            create_date_time = datetime.datetime.now().strftime(ConstantUtil.CREATE_DATE_FORMAT)
            # DAO 文件模板
            dao_template = jinja2_env.get_template("Dao_template.template")
            dao_content = dao_template.render(schema_name=schema,
                                              dao_import=dao_import,
                                              author=author,
                                              table_description=table_description,
                                              create_date_time=create_date_time,
                                              entity_name=entity_name,
                                              entity_name_first_lower=entity_name_first_lower,
                                              unique_key_entity_method=unique_key_query_methods)
            dao_file_name = f'{entity_name}Dao.java'
            write_file(dao_file_name, dao_content, file_save_dir)
            logger.info(f'successfully generate {table_name} of {schema} DAO')
        except Exception as e:
            logger.error(f'generation {table_name} of {schema} DAO has failed, error is:{e}')

    def auto_generate_mapper(self, **kwargs):
        """ Automatically generate mappers corresponding to database tables """

        schema = kwargs.get('schema', '')
        table_name = kwargs.get('table_name', '')
        entity_name = kwargs.get('entity_name', '')
        table_description = kwargs.get('table_description', f'{table_name} mapper')
        file_save_dir = kwargs.get("file_save_dir", "")
        column_definitions = kwargs.get('column_definitions', [])
        author = kwargs.get('author', 'auto generate')
        mysql_configuration = kwargs.get('mysql_configuration', None)
        logger.info(f'start to generate {table_name} of {schema} mybatis mapper')
        # mapper name
        mapper_name = f"{entity_name}Mapper"

        mapper_package = f'package com.hx.ylb.common.{schema}.mapper;'
        mapper_namespace = f'com.hx.ylb.common.repository.{schema}.mapper.{mapper_name}'
        entity_package = f'com.hx.ylb.common.entity.{schema}.{entity_name}'
        # mapper default import
        mapper_import_set = {entity_package,
                             'com.hx.ylb.common.repository.CrudRepository',
                             'org.springframework.stereotype.Repository',
                             'org.apache.ibatis.annotations.Param'}
        create_date = datetime.datetime.now().strftime(ConstantUtil.CREATE_DATE_FORMAT)
        class_description = ConstantUtil.JAVA_CLASS_DESCRIPTION_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                                                                         author=author,
                                                                                         description=table_description,
                                                                                         create_date=create_date)

        xml_mapper_crud_method = self.get_xml_mapper_crud_method(**{"schema": schema,
                                                                    "table": table_name,
                                                                    "mapper_namespace": mapper_namespace,
                                                                    "entity_package": entity_package,
                                                                    "column_definitions": column_definitions,
                                                                    "mysql_configuration": mysql_configuration})
        java_mapper_methods, unique_key_xml_method = get_default_methods(schema,
                                                                         table_name,
                                                                         entity_name,
                                                                         column_definitions,
                                                                         ConstantUtil.MAPPER_PARAM_MYBATIS_TEMPLATE,
                                                                         OrmCgEnum.ORM.ORM_MYBATIS.get_value(),)
        if java_mapper_methods:
            mapper_import_set.add("java.util.List")
            mapper_import_set.add("java.util.Collection")
        xml_mapper_methods = xml_mapper_crud_method + unique_key_xml_method
        java_mapper_file_name = f"{mapper_name}.java"
        mapper_import = self.classify_sort_java_import(mapper_import_set)
        java_mapper = ConstantUtil.JAVA_MAPPER_CLASS_TEMPLATE \
            .safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                             package=mapper_package,
                             mapper_import=mapper_import,
                             class_description=class_description,
                             class_name=f"{mapper_name} extends CrudRepository<{entity_name}>",
                             mapper_methods=java_mapper_methods)
        # generate java mapper
        write_file(java_mapper_file_name, java_mapper, file_save_dir)
        logger.info(f'successfully generate {table_name} of {schema} java mapper')
        result_map, base_column_list = self.mapper_xml_header(entity_package, column_definitions)
        xml_head = ConstantUtil.JAVA_MAPPER_XML_HEAD_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE)
        xml_mapper = ConstantUtil.MAPPER_XML_TEMPLATE.safe_substitute(NEW_LINE=ConstantUtil.NEW_LINE,
                                                                      mapper_xml_head=xml_head,
                                                                      name_space=mapper_namespace,
                                                                      result_map=result_map,
                                                                      base_column_List=base_column_list,
                                                                      mapper_methods=xml_mapper_methods)
        # generate xml mapper
        xml_file_name = mapper_name + '.xml'
        write_file(xml_file_name, xml_mapper, file_save_dir)
        logger.info(f'successfully generate {table_name} of {schema} xml mapper')
        # generate DAO file
        self.auto_generate_dao(schema,
                               entity_name,
                               table_name,
                               author,
                               table_description,
                               column_definitions,
                               file_save_dir)

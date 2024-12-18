# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: constants
@version: 1.0.0
@since: 2024/4/30 19:30
"""
import os
from string import Template

from ormcg.utils.enum_util import OrmCgEnum


class Invariable(object):
    class ConstError(PermissionError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__.keys():
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError("Can't unbind const(%s)" % name)
        raise NameError(name)


class EntitySuperClass(Invariable):
    def __init__(self, package, class_name, fields, inherit_word='extends', super_class=None, super_package=None):
        self.package = package
        self.class_name = class_name
        self.fields = fields
        self.inherit_word = inherit_word
        self.super_class = super_class
        self.super_package = super_package


class JavaTypeInfo(Invariable):
    def __init__(self, java_type, package, import_flag, alter_type=None, alter_package=None, alter_predicate=None):
        self.java_type = java_type
        self.package = package
        self.import_flag = import_flag
        self.alter_type = alter_type
        self.alter_package = alter_package
        self.alter_predicate = alter_predicate


class MethodParam(Invariable):
    """ java method param description"""

    def __init__(self, type_name, param_name, import_flag, column_name=None, db_data_type=None):
        # param type name
        self.type_name = type_name
        self.param_name = param_name
        self.import_flag = import_flag
        self.column_name = column_name
        self.db_data_type = db_data_type


class MybatisMapperMethod:
    """ mybatis mapper method description class"""

    def __init__(self, method_description, params, return_type, method_name, crud_type, crud_sub_type):
        self.method_description = method_description
        # method parameters
        self.params = params
        self.return_type = return_type
        self.method_name = method_name
        self.crud_type = crud_type
        self.crud_sub_type = crud_sub_type


class ConstantUtil(Invariable):
    # default chatset
    DEFAULT_CHARSET = 'utf-8'
    """ logger setting constants """
    LOG_FORMATTER = '%(asctime)s.%(msecs)03d %(levelname)s ' \
                    '[%(filename)s %(funcName)s line:%(lineno)d] %(' \
                    'message)s '
    LOG_DATE_TIME_FORMATTER = '%Y-%m-%d %H:%M:%S'
    LOG_FILE_MAX_SIZE = 500 * 1024 * 1024
    LOG_FILE_NAME = './ormcg.log'
    LOG_FILE_BACKUP_COUNT = 3

    # DB isolation level
    ISOLATION_LEVEL = 'REPEATABLE READ'

    # config file dir
    CONFIG_FILE_DIRECTORY = r'D:\hxWorkspace\ormcg\config'

    NEW_LINE = os.linesep

    CREATE_DATE_FORMAT = '%Y/%#m/%#d %H:%M'

    DEFAULT_PROP_PREFIX = 'entity.'

    JAVA_LONG_PACKAGE = 'java.lang.Long'
    JAVA_BYTE_PACKAGE = 'java.lang.Byte'
    JAVA_STRING_PACKAGE = 'java.lang.String'
    JAVA_DOUBLE_PACKAGE = 'java.lang.Double'
    JAVA_INTEGER_PACKAGE = 'java.lang.Integer'
    JAVA_BYTE_ARRAY_TYPE = 'Byte[]'

    MYSQL_JAVA_MAP = {
        'BIGINT': JavaTypeInfo('Long', JAVA_LONG_PACKAGE, False),
        'BIGINT UNSIGNED': JavaTypeInfo('Long', JAVA_LONG_PACKAGE, False),
        'BINARY': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'BIT': JavaTypeInfo('Boolean', 'java.lang.Boolean', False),
        'BLOB': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'BOOL': JavaTypeInfo('Boolean', ' java.lang.Boolean', False),
        'CHAR': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'DATE': JavaTypeInfo('Date', 'java.sql.Date', True),
        'DATETIME': JavaTypeInfo('Instant', 'java.time.Instant', True),
        'DECIMAL': JavaTypeInfo('BigDecimal', 'java.math.BigDecimal', True),
        'DOUBLE': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, False),
        'DOUBLE PRECISION': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, False),
        'DOUBLE PRECISION UNSIGNED': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, False),
        'DOUBLE UNSIGNED': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, False),
        'ENUM': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'FLOAT': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, False),
        'INT': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, '', True),
        'INT UNSIGNED': JavaTypeInfo('Long', JAVA_LONG_PACKAGE, False),
        'INTEGER': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, '', True),
        'INTEGER UNSIGNED': JavaTypeInfo('Long', JAVA_LONG_PACKAGE, False),
        'LONG VARBINARY': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'LONG VARCHAR': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'LONGBLOB': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'LONGTEXT': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'MEDIUMBLOB': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'MEDIUMINT': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, False),
        'MEDIUMINT UNSIGNED': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, False),
        'MEDIUMTEXT': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'NUMERIC': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, True),
        'REAL': JavaTypeInfo('Double', JAVA_DOUBLE_PACKAGE, True),
        'SET': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'SMALLINT': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, False),
        'SMALLINT UNSIGNED': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, False),
        'TEXT': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'TIME': JavaTypeInfo('Time', 'java.sql.Time', True),
        'TIMESTAMP': JavaTypeInfo('Instant', 'java.time.Instant', True),
        'TINYBLOB': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'TINYINT': JavaTypeInfo('Boolean', 'java.lang.Boolean', False),
        'TINYINT UNSIGNED': JavaTypeInfo('Integer', JAVA_INTEGER_PACKAGE, False),
        'TINYTEXT': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'VARBINARY': JavaTypeInfo(JAVA_BYTE_ARRAY_TYPE, JAVA_BYTE_PACKAGE, False),
        'VARCHAR': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
        'YEAR': JavaTypeInfo('Date', 'java.sql.Date', True),
        'JSON': JavaTypeInfo('String', JAVA_STRING_PACKAGE, False),
    }

    MYSQL_DATA_TYPE_JDBC_TYPE_MAP = {
        'BIGINT': 'BIGINT',
        'BIGINT UNSIGNED': 'BIGINT',
        'BINARY': 'BIGINT',
        'BIT': 'BIT',
        'BLOB': 'BINARY',
        'BOOL': 'BOOLEAN',
        'CHAR': 'CHAR',
        'DATE': 'DATE',
        'DATETIME': 'TIMESTAMP',
        'DECIMAL': 'DECIMAL',
        'DOUBLE': 'DOUBLE',
        'DOUBLE PRECISION': 'DOUBLE',
        'DOUBLE PRECISION UNSIGNED': 'DOUBLE',
        'DOUBLE UNSIGNED': 'DOUBLE',
        'ENUM': 'CHAR',
        'FLOAT': 'REAL',
        'INT': 'INTEGER',
        'INT UNSIGNED': 'INTEGER',
        'INTEGER': 'INTEGER',
        'INTEGER UNSIGNED': 'INTEGER',
        'LONG VARBINARY': 'LONGVARBINARY',
        'LONG VARCHAR': 'LONGVARCHAR',
        'LONGBLOB': 'LONGVARBINARY',
        'LONGTEXT': 'LONGVARCHAR',
        'MEDIUMBLOB': 'LONGVARBINARY',
        'MEDIUMINT': 'INTEGER',
        'MEDIUMINT UNSIGNED': 'INTEGER',
        'MEDIUMTEXT': 'LONGVARCHAR',
        'NUMERIC': 'DECIMAL',
        'REAL': 'REAL',
        'SET': 'CHAR',
        'SMALLINT': 'SMALLINT',
        'SMALLINT UNSIGNED': 'SMALLINT',
        'TEXT': 'LONGVARCHAR',
        'TIME': 'TIME',
        'TIMESTAMP': 'TIMESTAMP',
        'TINYBLOB': 'BINARY',
        'TINYINT': 'TINYINT',
        'TINYINT UNSIGNED': 'TINYINT',
        'TINYTEXT': 'VARCHAR',
        'VARBINARY': 'VARBINARY',
        'VARCHAR': 'VARCHAR',
        'YEAR': 'DATE',
        'json': 'unknown jdbcType, Please specify typeHandler instead',
    }

    JAVA_PACKAGE_TEMPLATE = Template('${prefix}com.hx.ylb.common.${kind_type}.${package}${suffix}')

    JAVA_ENTITY_DEFAULT_IMPORT = 'java.io.Serializable;'

    JAVA_CLASS_DESCRIPTION_TEMPLATE = Template('${NEW_LINE}'
                                               '/**'
                                               '${NEW_LINE} * @author ${author}'
                                               '${NEW_LINE} * @version 1.0.0'
                                               '${NEW_LINE} * @description ${description}'
                                               '${NEW_LINE} * @createDate ${create_date}'
                                               '${NEW_LINE} * @since 1.0.0'
                                               '${NEW_LINE} */')

    JAVA_ENTITY_CLASS_TEMPLATE = Template('${package}'
                                          '${NEW_LINE}'
                                          '${NEW_LINE}'
                                          '${entity_import}'
                                          '${NEW_LINE}'
                                          '${class_description}'
                                          '${NEW_LINE}'
                                          '${class_annotations}'
                                          'public class ${class_name} ${inherit_word} ${super_class} {'
                                          '${entity_fields}'
                                          '${getter_setter_methods}'
                                          '${to_string_method}'
                                          '${NEW_LINE}}')

    JAVA_CLASS_FIELD_TEMPLATE = Template('${NEW_LINE}'
                                         '${NEW_LINE}    /**'
                                         '${NEW_LINE}     * ${comment}'
                                         '${NEW_LINE}     */'
                                         '${field_annotation}'
                                         '${NEW_LINE}    private ${field_type} ${field_name};')

    JAVA_CLASS_GETTER_TEMPLATE = Template('${NEW_LINE}'
                                          '${NEW_LINE}    public ${field_type} ${getter}() {'
                                          '${NEW_LINE}        return ${field_name};'
                                          '${NEW_LINE}    }')

    JAVA_CLASS_SETTER_TEMPLATE = Template('${NEW_LINE}'
                                          '${NEW_LINE}    public void ${setter}(${field_type} ${'
                                          'field_name}) { '
                                          '${NEW_LINE}        this.${field_name} = ${field_name};'
                                          '${NEW_LINE}    }')

    JAVA_TO_STRING_TEMPLATE = Template('                ", ${field_name_left}=${enclose_left}" + '
                                       '${field_name_right}${enclose_right} +'
                                       )

    JAVA_CLASS_TO_STRING_METHOD_TEMPLATE = Template('${NEW_LINE}'
                                                    '${NEW_LINE}'
                                                    '    @Override'
                                                    '${NEW_LINE}    public String toString() {'
                                                    '${NEW_LINE}        return "${class_name}{" +'
                                                    '${NEW_LINE}${to_string}'
                                                    '                \'}\';'
                                                    '${NEW_LINE}    }')

    AUDITING_COLUMN_SET = {'created_by', 'created_date', 'last_modified_by', 'last_modified_date'}

    AUDITING_FIELD_SET = {'createdBy', 'createdDate', 'lastModifiedBy', 'lastModifiedDate'}

    JAVA_MAPPER_CLASS_TEMPLATE = Template('${package}'
                                          '${NEW_LINE}'
                                          '${NEW_LINE}'
                                          '${mapper_import}'
                                          '${NEW_LINE}'
                                          '${class_description}'
                                          '${NEW_LINE}@Repository'
                                          '${NEW_LINE}'
                                          'public interface ${class_name} {'
                                          '${mapper_methods}'
                                          '${NEW_LINE}}')

    JAVA_MAPPER_METHOD_TEMPLATE = Template('${NEW_LINE}'
                                           '${NEW_LINE}    /**'
                                           '${NEW_LINE}     * ${method_description}'
                                           '${NEW_LINE}     *'
                                           '${param_description}'
                                           '${NEW_LINE}     * @return ${return_type}'
                                           '${NEW_LINE}     */'
                                           '${NEW_LINE}    ${return_type} ${method_name}(${param_list});')

    JAVACLASS_METHOD_PARAM_DESCRIPTION_TEMPLATE = Template('${NEW_LINE}     * @param ${param_name} ${param_type}')

    METHOD_PARAM_TEMPLATE = Template('${entity_name} ${entity_name_first_lower}')
    MYBATIS_FIXED_METHODS = [
        MybatisMapperMethod('Dynamically add new records, and if the entity object field is not set to a value,'
                            ' the corresponding column will not be inserted during insertion',
                            [],
                            'int', 'saveDynamically', OrmCgEnum.CrudType.CRUD_TYPE_INSERT,
                            OrmCgEnum.CrudSubType.CRUD_SUB_TYPE_INSERT_DYNAMICAL),

        MybatisMapperMethod('Simply add a new record, and the field value of the entity class object is'
                            ' the value of the corresponding column at the time of insertion',
                            [],
                            'int', 'saveUsually', OrmCgEnum.CrudType.CRUD_TYPE_INSERT,
                            OrmCgEnum.CrudSubType.CRUD_SUB_TYPE_INSERT_USUAL),

        MybatisMapperMethod('Batch insert records',
                            [],
                            'int', 'saveAll', OrmCgEnum.CrudType.CRUD_TYPE_INSERT,
                            OrmCgEnum.CrudSubType.CRUD_SUB_TYPE_INSERT_BATCH),

        MybatisMapperMethod('动态地更新记录, 实体类对象字段不设值则更新时对应列不更新',
                            [],
                            'int', 'updateByIdDynamically', OrmCgEnum.CrudType.CRUD_TYPE_UPDATE,
                            OrmCgEnum.CrudSubType.CRUD_SUB_TYPE_UPDATE_DYNAMICAL),

        MybatisMapperMethod('Dynamically update records, if the entity class object field is not set to a value,'
                            ' the corresponding column will not be updated when updated',
                            [],
                            'int', 'updateByIdUsually', OrmCgEnum.CrudType.CRUD_TYPE_UPDATE,
                            OrmCgEnum.CrudSubType.CRUD_SUB_TYPE_UPDATE_USUAL),

        MybatisMapperMethod('Dynamically query records, if the entity class object field is not set to a value,'
                            ' the corresponding column is not used as a query condition',
                            [],
                            'List<entity_name>', 'findAll', OrmCgEnum.CrudType.CRUD_TYPE_SELECT,
                            OrmCgEnum.CrudSubType.CRUD_SUB_TYPE_SELECT_BY_DYNAMICAL_CONDITION),
    ]

    JAVA_MAPPER_XML_HEAD_TEMPLATE = Template('<?xml version="1.0" encoding="utf-8" ?>'
                                             '${NEW_LINE}<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper '
                                             '3.0//EN"${NEW_LINE} '
                                             '        "http://mybatis.org/dtd/mybatis-3-mapper.dtd">')

    JAVA_MAPPER_XML_RESULT_MAPPING_TEMPLATE = Template('${NEW_LINE}        '
                                                       '<${result_type} column="${column}" property="${property}" '
                                                       'jdbcType="${jdbcType}"/>')

    JAVA_MAPPER_XML_RESULT_MAP_TEMPLATE = Template('${NEW_LINE}    '
                                                   '<resultMap id="BaseResultMap" type="${entity_package}">'
                                                   '${mapping}'
                                                   '${NEW_LINE}    </resultMap>')

    JAVA_MAPPER_BASE_COLUMN_TEMPLATE = Template('${NEW_LINE}        '
                                                '${column},')

    JAVA_MAPPER_BASE_COLUMN_LIST_TEMPLATE = Template('${NEW_LINE}    '
                                                     '<sql id="Base_Column_List">'
                                                     '${columns}'
                                                     '${NEW_LINE}    </sql>')

    MAPPER_XML_INSERT_IF_TEMPLATE = Template('${NEW_LINE}'
                                             '            <if test="${property_name} != null${non_null_and}">'
                                             '${NEW_LINE}               ${prefix}${column_or_property_name}${suffix}'
                                             '${NEW_LINE}            </if>')

    MAPPER_XML_USUAL_UPDATE_TEMPLATE = Template('${NEW_LINE}'
                                                '${comment}'
                                                '            ${column_name} = #{${prefix}${property_name}}${suffix}')

    MAPPER_XML_DYNAMICAL_UPDATE_IF_TEMPLATE = Template('${NEW_LINE}            '
                                                       '<if test="${property_name} != null${non_null_and}">'
                                                       '${pre_handler}'
                                                       '${NEW_LINE}                ${prefix}${column_name} '
                                                       '${operator} #{${property_name}}${suffix}'
                                                       '${NEW_LINE}            </if>')

    MAPPER_XML_INSERT_DYNAMICAL_TEMPLATE = Template('${NEW_LINE}'
                                                    '${NEW_LINE}    <!-- ${method_description} -->'
                                                    '${NEW_LINE}    <insert id="${method_name}">'
                                                    '${NEW_LINE}        INSERT INTO ${db}.${table}'
                                                    '${NEW_LINE}        <trim prefix="(" suffix=")" '
                                                    'suffixOverrides=",">'
                                                    '${column_list}'
                                                    '${NEW_LINE}        </trim>'
                                                    '${NEW_LINE}        <trim prefix="VALUES (" suffix=")" '
                                                    'suffixOverrides=",">'
                                                    '${property_list}'
                                                    '${NEW_LINE}        </trim>'
                                                    '${NEW_LINE}    </insert>')

    MAPPER_XML_UPDATE_DYNAMICAL_TEMPLATE = Template('${NEW_LINE}'
                                                    '${NEW_LINE}    <!-- ${method_description} -->'
                                                    '${NEW_LINE}    <update id="${method_name}">'
                                                    '${NEW_LINE}        UPDATE ${db}.${table}'
                                                    '${NEW_LINE}        <set>'
                                                    '${column_property_list}'
                                                    '${NEW_LINE}        </set>'
                                                    '${criteria_comment}'
                                                    '${NEW_LINE}        WHERE id = #{id} ${extra_criteria}'
                                                    '${NEW_LINE}    </update>')

    MAPPER_XML_INSERT_USUAL_COLUMN_TEMPLATE = Template('${NEW_LINE}             ${column},')

    MAPPER_XML_INSERT_USUAL_PROPERTY_TEMPLATE = Template('${NEW_LINE}             #{${prefix}${property_name}},')

    MAPPER_XML_INSERT_USUAL_TEMPLATE = Template('${NEW_LINE}'
                                                '${NEW_LINE}    <!-- ${method_description} -->'
                                                '${NEW_LINE}    <insert id="${method_name}">'
                                                '${NEW_LINE}        INSERT INTO ${db}.${table}'
                                                '${NEW_LINE}            ('
                                                '${column_list}'
                                                '${NEW_LINE}             ) VALUES'
                                                '${NEW_LINE}             ('
                                                '${property_list}'
                                                '${NEW_LINE}             )'
                                                '${NEW_LINE}    </insert>')

    MAPPER_XML_INSERT_BATCH_TEMPLATE = Template('${NEW_LINE}'
                                                '${NEW_LINE}    <!-- ${method_description} -->'
                                                '${NEW_LINE}    <insert id="${method_name}">'
                                                '${NEW_LINE}        INSERT INTO ${db}.${table}'
                                                '${NEW_LINE}            ('
                                                '${column_list}'
                                                '${NEW_LINE}             ) VALUES'
                                                '${NEW_LINE}        <foreach collection="${param_name}" item="entity" '
                                                'separator=","> '
                                                '${NEW_LINE}            ('
                                                '${property_list}'
                                                '${NEW_LINE}             )'
                                                '${NEW_LINE}        </foreach>'
                                                '${NEW_LINE}    </insert>')

    MAPPER_XML_INSERT_BATCH_DYNAMICALLY_TEMPLATE = Template('${NEW_LINE}'
                                                            '${NEW_LINE}    <!-- ${method_description} -->'
                                                            '${NEW_LINE}    <insert id="${method_name}">'
                                                            '${NEW_LINE}        <foreach collection="${param_name}"'
                                                            ' item="entity" separator=";"> '
                                                            '${NEW_LINE}            INSERT INTO ${db}.${table}'
                                                            '${NEW_LINE}            <trim prefix="(" suffix=")" '
                                                            'suffixOverrides=",">'
                                                            '${column_list}'
                                                            '${NEW_LINE}            </trim>'
                                                            '${NEW_LINE}            <trim prefix="VALUES (" suffix=")" '
                                                            'suffixOverrides=",">'
                                                            '${property_list}'
                                                            '${NEW_LINE}            </trim>'
                                                            '${NEW_LINE}         </foreach>'
                                                            '${NEW_LINE}    </insert>'
                                                            )

    MAPPER_XML_UPDATE_BATCH_DYNAMICALLY_TEMPLATE = Template('${NEW_LINE}'
                                                            '${NEW_LINE}    <!-- ${method_description} -->'
                                                            '${NEW_LINE}    <update id="${method_name}">'
                                                            '${NEW_LINE}        <foreach collection="${param_name}"'
                                                            ' item="entity" separator=";"> '
                                                            '${NEW_LINE}            UPDATE ${db}.${table}'
                                                            '${NEW_LINE}            <set>'
                                                            '    ${column_property_list}'
                                                            '${NEW_LINE}            </set>'
                                                            '${NEW_LINE}            '
                                                            'WHERE id = #{entity.id} ${extra_criteria}'
                                                            '${NEW_LINE}         </foreach>'
                                                            '${NEW_LINE}    </update>')

    MAPPER_XML_UPDATE_BATCH_USUALLY_TEMPLATE = Template('${NEW_LINE}'
                                                        '${NEW_LINE}    <!-- ${method_description} -->'
                                                        '${NEW_LINE}    <update id="${method_name}">'
                                                        '${NEW_LINE}        <foreach collection="${param_name}"'
                                                        ' item="entity" separator=";"> '
                                                        '${NEW_LINE}            UPDATE ${db}.${table}'
                                                        '${NEW_LINE}            SET'
                                                        '    ${column_property_list}'
                                                        '${NEW_LINE}            '
                                                        'WHERE id = #{entity.id} ${extra_criteria}'
                                                        '${NEW_LINE}         </foreach>'
                                                        '${NEW_LINE}    </update>')

    MAPPER_XML_UPDATE_USUAL_TEMPLATE = Template('${NEW_LINE}'
                                                '${NEW_LINE}    <!-- ${method_description} -->'
                                                '${NEW_LINE}    <update id="${method_name}">'
                                                '${NEW_LINE}        UPDATE ${db}.${table}'
                                                '${NEW_LINE}        SET'
                                                '${column_property_list}'
                                                '${criteria_comment}'
                                                '${NEW_LINE}        WHERE id = #{id} ${extra_criteria}'
                                                '${NEW_LINE}    </update>')

    MAPPER_XML_SELECT_BY_DYNAMICAL_CONDITION_TEMPLATE = Template('${NEW_LINE}'
                                                                 '${NEW_LINE}    <!-- ${method_description} -->'
                                                                 '${NEW_LINE}    <select id="${method_name}" '
                                                                 'resultMap="BaseResultMap"> '
                                                                 '${NEW_LINE}        SELECT '
                                                                 '${NEW_LINE}        '
                                                                 '<include refid="Base_Column_List"/>'
                                                                 '${NEW_LINE}        FROM ${db}.${table}'
                                                                 '${NEW_LINE}        <where>'
                                                                 '           ${dynamical_condition}'
                                                                 '${NEW_LINE}        </where>'
                                                                 '${NEW_LINE}    </select>')

    MAPPER_XML_SELECT_FIND_BY_UNIQUE_KEYS_TEMPLATE = Template('${NEW_LINE}'
                                                             '${NEW_LINE}    <!-- ${method_description} -->'
                                                             '${NEW_LINE}    <select id="${method_name}" '
                                                             'resultMap="BaseResultMap"> '
                                                             '${NEW_LINE}        SELECT '
                                                             '${NEW_LINE}        '
                                                             '<include refid="Base_Column_List"/>'
                                                             '${NEW_LINE}        FROM ${db}.${table}'
                                                             '${NEW_LINE}        <where>'
                                                             '${NEW_LINE}           ${dynamical_condition}'
                                                             '${NEW_LINE}        </where>'
                                                             '${NEW_LINE}    </select>')

    MAPPER_XML_SELECT_FIND_BY_FOREACH_TEMPLATE = Template('${NEW_LINE}            '
                                                          '${column_name} IN '
                                                          '${NEW_LINE}            <foreach collection="${'
                                                          'key_collection}" '
                                                          'item="${key_name}" '
                                                          'open="(" separator="," close=")">'
                                                          '${NEW_LINE}                 #{${key_name}}'
                                                          '${NEW_LINE}            </foreach>')

    MAPPER_XML_LIKE_QUERY_BIND_TEMPLATE = Template('${NEW_LINE}                '
                                                   '<bind name="${bind_name}" value="\'%\'+ ${property_name} + \'%\'" '
                                                   '/>')

    MAPPER_XML_TEMPLATE = Template('${mapper_xml_head}'
                                   '${NEW_LINE}<mapper namespace="${name_space}">'
                                   '${result_map}'
                                   '${NEW_LINE}${base_column_List}'
                                   '${mapper_methods}'
                                   '${NEW_LINE}</mapper>')

    MAPPER_XML_SELECT_FIND_BY_UNIQUE_KEY_TEMPLATE = Template('${NEW_LINE}            '
                                                          '${column_name} = #{${field_name}}')

    MAPPER_PARAM_MYBATIS_TEMPLATE = Template('@Param("${param_name}") ${param_type} ${param_name}')
    MAPPER_PARAM_JPA_TEMPLATE = Template('${param_type} ${param_name}')


    INSET_EXCLUDE_COLUMN_SET = {'id', 'last_modified_by', 'last_modified_date'}

    UPDATE_EXCLUDE_COLUMN_SET = {'id', 'created_by', 'created_date'}

    NON_NULL_AND_STRING_SET = {'String'}

    NON_NULL_AND_STRING_TEMPLATE = Template(" and ${property_name} != ''")

    PROPERTY_VALID_AND_NUMERICAL_SET = {'Integer', 'Long', 'Double', 'BigDecimal'}

    NON_NULL_AND_NUMERICAL_TEMPLATE = Template(" and ${property_name} gt 0")

    NON_NULL_VALID_AND_OTHER_SET = {'Instant', 'Date', 'Time', 'Boolean', JAVA_BYTE_ARRAY_TYPE}

    UNIQUE_COLUMN_KEYS = {'PRI', 'UNI'}

    COLUMN_NAME_ABBREVIATION_REPLACE = {'cn': 'chinese', 'en': 'english'}

    QUERY_CONDITION_CHAR_MAX_LENGTH = 16

    LIKE_QUERY_COLUMN_KEY_WORD_SET = {'code', 'name', 'title'}

    ENTITY_SUPER_CLASS_MAP = {
        'AbstractId': EntitySuperClass('com.hx.ylb.common.entity.AbstractId', 'AbstractId',
                                       {'id'},
                                       'extends',
                                       'Serializable',
                                       'java.io.Serializable'
                                       ),
        'AbstractAuditing': EntitySuperClass('com.hx.ylb.common.entity.AbstractAuditing',
                                             'AbstractAuditing',
                                             {'id',
                                              'createdBy',
                                              'createdDate',
                                              'lastModifiedBy',
                                              'lastModifiedDate'},
                                             'extends',
                                             'AbstractId',
                                             'com.hx.ylb.common.entity.AbstractId'),

    }

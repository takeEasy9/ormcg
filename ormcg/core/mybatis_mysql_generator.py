# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description:
@version: 1.0.0
@since: 2024/4/30 19:59
"""
from sqlalchemy import and_

from ormcg.config.logger_config import logger
from ormcg.config.mysql_config import MysqlConfiguration
from ormcg.core.mybatis_generator import MyBatisGenerator
from ormcg.core.orm_generator import auto_generate_java_entity
from ormcg.db.mysql.mysql_information_schema_models import MysqlTablesModel, MysqlColumnsModel, MysqlStatisticsModel
from ormcg.utils.enum_util import OrmCgEnum
from ormcg.utils.string_util import first_upper_case, to_camel_case


class MybatisMysqlGenerator(MyBatisGenerator):

    def auto_generate(self, **kwargs):
        print(kwargs)
        env = kwargs.get('env', "dev")
        schema_name = kwargs.get('schema', None)
        table_name = kwargs.get('table_name', None)
        try:
            mysql_configuration = MysqlConfiguration(env)
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
                column_definitions = self.mysql_to_column_definition(columns, index_name_columns_dict)
                kwargs['column_definitions'] = column_definitions
                # generate entity
                auto_generate_java_entity(**kwargs)
                if kwargs.get('orm', 'mybatis') == OrmCgEnum.ORM.ORM_MYBATIS.get_value():
                    # generate mybatis template code
                    kwargs['entity_name'] = first_upper_case(to_camel_case(table_name))
                    self.auto_generate_mapper(**kwargs)

        except Exception as e:
            logger.error(f'mysql：{table_name} of {schema_name} mybatis template code generation has failed,'
                         f' error is：{e}')

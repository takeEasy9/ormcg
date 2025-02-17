# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: generator 配置
@version: 1.0.0
@since: 2025/2/13 21:49
"""
import os

import yaml

from ormcg.config.logger_config import logger
from ormcg.utils.constant_util import ConstantUtil
from ormcg.utils.file_util import get_current_work_dir


class OrmCgConfiguration:

    def __init__(self, env=None, schema='ormcg'):
        work_dir = get_current_work_dir()
        profile_file = os.path.join(work_dir, 'config', 'ormcg.yaml')
        logger.info(f'Starting to load ormcg configuration information in the path: {profile_file}')
        with open(profile_file, mode='r', encoding=ConstantUtil.DEFAULT_CHARSET) as f:
            config_setting = yaml.load(f, Loader=yaml.FullLoader)
            if env is None:
                db_env = config_setting['profiles']['active']
            else:
                db_env = env
            logger.info(f'Starting to load {db_env} environment database configuration')
            # DB 配置
            self.meta_db_name = config_setting['db'][db_env]['mysql_server']['db_name']
            self.meta_db_host = config_setting['db'][db_env]['mysql_server']['host']
            self.meta_db_port = config_setting['db'][db_env]['mysql_server']['port']
            self.meta_db_username = config_setting['db'][db_env]['mysql_server']['username']
            self.meta_db_password = config_setting['db'][db_env]['mysql_server']['password']
            self.insert_exclude_columns = set(config_setting['db'][db_env]['mysql_server']['insert_exclude_columns'])
            self.update_exclude_columns = set(config_setting['db'][db_env]['mysql_server']['update_exclude_columns'])
            self.select_where_exclude_columns = set(config_setting['db'][db_env]['mysql_server']
                                                    ['select_where_exclude_columns'])
            self.version_control_column = config_setting['db'][db_env]['mysql_server']['version_control_column']
            self.exclude_schema_name = config_setting['db'][db_env]['exclude_schema_name']
            self.meta_isolation_level = config_setting['db'][db_env]['isolation_level']
            self.meta_max_overflow = config_setting['db'][db_env]['max_overflow']
            self.meta_pool_size = config_setting['db'][db_env]['pool_size']
            self.meta_pool_timeout = config_setting['db'][db_env]['pool_timeout']
            self.meta_pool_recycle = config_setting['db'][db_env]['pool_recycle']

            java_version = config_setting['orm']['java']['version']
            valid_versions = [8, 9, 11, 17, 21]
            if java_version not in valid_versions:
                java_version = 11
            self.orm_java_version = java_version
            self.entity_super_classes = config_setting['orm']['entity_super_classes']
            # 默认值
            default_entity_package = f'com.{schema}.entity'

            # 读取 MyBatis 相关配置
            self.orm_mybatis_entity_package = config_setting['orm']['mybatis']['entity']['package'] \
                if config_setting['orm']['mybatis']['entity']['package'] else default_entity_package
            self.orm_mybatis_entity_path = config_setting['orm']['mybatis']['entity']['path'] if \
                config_setting['orm']['mybatis']['entity']['path'] else schema
            self.orm_mybatis_mapper_package = config_setting['orm']['mybatis']['mapper']['package'] \
                if config_setting['orm']['mybatis']['mapper']['package'] else f'com.{schema}.mapper'
            self.orm_mybatis_mapper_path = config_setting['orm']['mybatis']['mapper']['path'] \
                if config_setting['orm']['mybatis']['mapper']['path'] else schema
            self.orm_mybatis_dao_package = config_setting['orm']['mybatis']['dao']['package'] \
                if config_setting['orm']['mybatis']['dao']['package'] else f'com.{schema}.dao'
            self.orm_mybatis_dao_path = config_setting['orm']['mybatis']['dao']['path'] if config_setting['orm']['mybatis']['dao'][
                'path'] else schema
            # 读取 JPA 相关配置
            self.orm_jpa_entity_package = config_setting['orm']['jpa']['entity']['package'] \
                if config_setting['orm']['jpa']['entity']['package'] else default_entity_package
            self.orm_jpa_entity_path = config_setting['orm']['jpa']['entity']['path'] \
                if config_setting['orm']['jpa']['entity']['path'] else schema
            self.orm_jpa_repository_package = config_setting['orm']['jpa']['repository']['package'] \
                if config_setting['orm']['jpa']['repository']['package'] else f'com.{schema}.repository'
            self.orm_jpa_repository_path = config_setting['orm']['jpa']['repository']['path']\
                if config_setting['orm']['jpa']['repository']['path'] else schema
            logger.info('ormcg configuration file loading completed')

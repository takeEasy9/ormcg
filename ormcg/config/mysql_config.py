# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description:
@version: 1.0.0
@since: 2024/4/30 20:08
"""
import os
from contextlib import contextmanager
from urllib.parse import quote_plus

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from ormcg.config.logger_config import logger
from ormcg.utils.constant_util import ConstantUtil
from ormcg.utils.file_util import get_current_work_dir


class MysqlConfiguration:

    def __init__(self, env=None):
        work_dir = get_current_work_dir()
        profile_file = os.path.join(work_dir, 'config', 'ormcg.yaml')
        logger.info(f'Starting to load MySQL database configuration information in the path: {profile_file}')
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
            self.exclude_schema_name = config_setting['db'][db_env]['exclude_schema_name']
            self.meta_isolation_level = config_setting['db'][db_env]['isolation_level']
            self.meta_max_overflow = config_setting['db'][db_env]['max_overflow']
            self.meta_pool_size = config_setting['db'][db_env]['pool_size']
            self.meta_pool_timeout = config_setting['db'][db_env]['pool_timeout']
            self.meta_pool_recycle = config_setting['db'][db_env]['pool_recycle']
            logger.info('MySQL configuration file loading completed')

        logger.info('Starting to create <mysql information_schema> sqlalchemy engine')
        meta_uri = f'mysql+pymysql://{quote_plus(self.meta_db_username)}:' \
                   f'{quote_plus(self.meta_db_password)}' \
                   f'@{self.meta_db_host}:' \
                   f'{self.meta_db_port}' \
                   f'/{self.meta_db_name}?charset=utf8'
        # db engine
        engine = create_engine(meta_uri,
                               echo=False,
                               isolation_level=self.meta_isolation_level,
                               max_overflow=self.meta_max_overflow,
                               pool_size=self.meta_pool_size,
                               pool_timeout=self.meta_pool_timeout,
                               pool_recycle=self.meta_pool_recycle)
        self.engine = engine
        # session factory
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.__session = scoped_session(session_factory)

    @contextmanager
    def session_factory(self, auto_commit=False):
        try:
            yield self.__session
            if auto_commit:
                self.__session.commit()
        except Exception as error:
            logger.critical(f'sqlalchemy session error: {error}')
            self.__session.rollback()
            raise
        finally:
            self.__session.close()

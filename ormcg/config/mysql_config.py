# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description:
@version: 1.0.0
@since: 2024/4/30 20:08
"""
from contextlib import contextmanager
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from ormcg.config.logger_config import logger
from ormcg.config.ormcg_config import OrmCgConfiguration


class MysqlConfiguration:

    def __init__(self, orm_configuration: OrmCgConfiguration):
        logger.info('Starting to create <mysql information_schema> sqlalchemy engine')
        meta_uri = f'mysql+pymysql://{quote_plus(orm_configuration.meta_db_username)}:' \
                   f'{quote_plus(orm_configuration.meta_db_password)}' \
                   f'@{orm_configuration.meta_db_host}:' \
                   f'{orm_configuration.meta_db_port}' \
                   f'/{orm_configuration.meta_db_name}?charset=utf8'
        # db engine
        engine = create_engine(meta_uri,
                               echo=False,
                               isolation_level=orm_configuration.meta_isolation_level,
                               max_overflow=orm_configuration.meta_max_overflow,
                               pool_size=orm_configuration.meta_pool_size,
                               pool_timeout=orm_configuration.meta_pool_timeout,
                               pool_recycle=orm_configuration.meta_pool_recycle)
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

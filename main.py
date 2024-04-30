# -*- coding: utf-8 -*-

"""
@author: takeEasy9
@description: startup file
@version: 1.0.0
@since: 2024/4/30 19:17
"""

import argparse
import os.path

from ormcg.config.logger_config import logger
from ormcg.core.mybatis_mysql_generator import MybatisMysqlGenerator
from ormcg.utils.file_util import get_current_work_dir

if __name__ == '__main__':
    try:
        # command line args
        parser = argparse.ArgumentParser(description='help to autogenerate orm code like mybatis mapper')
        parser.add_argument('-A', '--author',
                            default='autogenerate',
                            help='who generate this code')
        parser.add_argument('-E', '--env', choices=['dev', 'test', 'prod'],
                            default='dev',
                            help='database environment, available options [dev, test, product]')
        parser.add_argument('-D', '--db', choices=['mysql', 'oracle', 'clickhouse'],
                            default='mysql',
                            help='what kind of database you are using')
        parser.add_argument('-H', '--host', help='the host of target database')
        parser.add_argument('-p', '--port', type=int, help='the port of target database')
        parser.add_argument('-S', '--schema', default='analysis',
                            help='the schema that table you want to autogenerate orm code belong to')
        parser.add_argument('table', help='the table that you want to autogenerate orm code')
        parser.add_argument('table_description', help='the description of table')
        # Parsing command-line parameters
        args = parser.parse_args()
        work_dir = get_current_work_dir()
        file_save_dir = os.path.join(work_dir, args.schema)
        logger.info(f'command line args: env={args.env} db={args.db} '
                    f'host={args.host} port={args.port} schema={args.schema}'
                    f' table={args.table} table_description={args.table_description},'
                    f'work dir: {work_dir}, The path to save the generated file is {file_save_dir}')
        mysqlMybatisGenerator = MybatisMysqlGenerator()
        kwargs = {"env": args.env, 'schema': args.schema, 'table_name': args.table,
                  'author': args.author,
                  'table_description': args.table_description,
                  'work_dir': work_dir,
                  "file_save_dir": file_save_dir}
        # kwargs = {'schema': "cms", 'table_name': "cms_news",
        #           'author': "args.author",
        #           'table_description': "args.table_description", }
        mysqlMybatisGenerator.auto_generate(**kwargs)
    except Exception as e:
        logger.error(f'orm code generation failed, error cause is: {e}')

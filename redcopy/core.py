from redshift_connector import connect, Connection, error
from redcopy.utils import get_ddl, data_io
from . import logger


def get_table_list(connection: Connection):
    tables_cur = connection.cursor()
    tables_cur.execute("""
        SELECT table_schema, table_name FROM information_schema.tables 
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'temp')
        ORDER BY table_schema, table_name
        """)
    tables = tables_cur.fetchall()
    tables_cur.close()
    logger.info(f'{len(tables)} tables found')
    return tables


def get_src_ddl(connection: Connection):
    logger.info(f'Fetching table DDL')
    tables = get_ddl.get_table_ddl(connection=connection)
    logger.info(f'DDL for {len(tables)} tables extracted')
    return tables


def execute_ddl(connection: Connection, ddl: dict):
    logger.info('Executing DDL on destination')
    connection.autocommit = True
    for table, ddl in ddl.items():
        logger.info(f'Running DDL for {table}')
        cur = connection.cursor()
        try:
            cur.execute(ddl)
            logger.info(f'{table} created')
        except error.ProgrammingError as e:
            logger.error(e)
            connection.rollback()
        cur.close()


def unload_source(connection: Connection, iam_role_arn: str, s3_path: str):
    data_io.unload_tables_to_s3(connection=connection,
                                iam_role_arn=iam_role_arn,
                                s3_path=s3_path)


def load_target(connection: Connection, iam_role_arn: str, s3_path: str):
    data_io.load_tables_from_s3(connection=connection,
                                iam_role_arn=iam_role_arn,
                                s3_path=s3_path)

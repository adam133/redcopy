from redshift_connector import connect, Connection, error
from redcopy.utils import get_ddl, data_io
import logging

logging.basicConfig(level=logging.INFO)


def get_table_list(connection: Connection):
    tables_cur = connection.cursor()
    tables_cur.execute("""
        SELECT table_schema, table_name FROM information_schema.tables 
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'temp')
        ORDER BY table_schema, table_name
        """)
    tables = tables_cur.fetchall()
    tables_cur.close()
    logging.info(f'{len(tables)} tables found')
    return tables


def get_src_ddl(connection: Connection):
    logging.info(f'Fetching table DDL')
    tables = get_ddl.get_table_ddl(connection=connection)
    logging.info(f'DDL for {len(tables)} tables extracted')
    return tables


def execute_ddl(connection: Connection, ddl: dict):
    logging.info('Executing DDL on destination')
    connection.autocommit = True
    for table, ddl in ddl.items():
        logging.info(f'Running DDL for {table}')
        cur = connection.cursor()
        try:
            cur.execute(ddl)
            logging.info(f'{table} created')
        except error.ProgrammingError as e:
            logging.error(e)
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

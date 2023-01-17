from redshift_connector import Connection
from redcopy import core, logger


def get_table_ddl(connection: Connection):
    tables = core.get_table_list(connection=connection)
    table_ddl = dict()
    for table_schema, table_name in tables:
        show_table_cur = connection.cursor()
        logger.info(f'Fetching DDL for {table_schema}.{table_name}')
        show_table_cur.execute(f'SHOW TABLE {table_schema}.{table_name}')
        ddl = show_table_cur.fetchone()[0].replace('CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ')
        table_ddl[f'{table_schema}.{table_name}'] = ddl
    return table_ddl

from redshift_connector import Connection, error
from redcopy import core, logger


def unload_tables_to_s3(connection: Connection, iam_role_arn: str, s3_path: str):
    # ensure s3_path ends with a /
    assert s3_path[-1] == '/'
    tables = core.get_table_list(connection=connection)
    logger.info(f'Unloading to s3 path: {s3_path}')
    connection.autocommit = True
    for table_schema, table_name in tables:
        logger.info(f'Unloading table {table_schema}.{table_name}')
        unload_cur = connection.cursor()
        unload_sql = f"""
        unload ('select * from {table_schema}.{table_name}')
        to '{s3_path}{table_schema}/{table_name}/' iam_role '{iam_role_arn}'
        parquet manifest allowoverwrite
        """
        unload_cur.execute(unload_sql)
        unload_cur.close()


def load_tables_from_s3(connection: Connection, iam_role_arn: str, s3_path: str):
    # ensure s3_path ends with a /
    assert s3_path[-1] == '/'
    tables = core.get_table_list(connection=connection)
    logger.info(f'Loading tables from s3 path: {s3_path}')
    connection.autocommit = True

    for table_schema, table_name in tables:
        logger.info(f'Loading table {table_schema}.{table_name}')
        load_cur = connection.cursor()
        load_sql = f"""
        copy {table_schema}.{table_name}
        from '{s3_path}{table_schema}/{table_name}/manifest' 
        iam_role '{iam_role_arn}' format as parquet manifest
        """
        try:
            load_cur.execute(load_sql)
        except error.ProgrammingError as e:
            logger.error(e)
            connection.rollback()
        load_cur.close()

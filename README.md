# Redcopy

[![image](https://img.shields.io/pypi/v/redcopy.svg)](https://pypi.python.org/pypi/redcopy)
[![image](https://img.shields.io/pypi/l/redcopy.svg)](https://pypi.python.org/pypi/redcopy)
[![image](https://img.shields.io/pypi/pyversions/redcopy.svg)](https://pypi.python.org/pypi/redcopy)

A simple Python library for easily making a copy of a Redshift Database on the same or different instance.


## Development

Create virtual environment
```
python3 -m venv venv
source ./venv/bin/activate
```

Install
```
pip install redcopy
```

### Basic usage
Redcopy uses [redshift-connector](https://pypi.org/project/redshift-connector/) for interacting with the Redshift cluster

To start using, create a connection following the redshift-connector convention:
```
from redcopy import core
src = core.connect(host='your-connection-info',
                   ...)
```
Then pass this connection to fetch table DDL. This will return a dict in the form of:
`{'schema.tablename': 'CREATE TABLE ... '}`
```
src_ddl = core.get_src_ddl(connection=src)
```
Then you can execute that DDL:
```
core.execute_ddl(connection=dest, ddl=src_ddl)
```
To export and import actual data:
```
core.unload_source(connection=src,
                   iam_role_arn='your-iam-role',
                   s3_path='s3://your-s3-path/')
core.load_target(connection=dest,
                 iam_role_arn='your-iam-role',
                 s3_path='s3://your-s3-path/')
```

## Future work:

- Add automated tests
- Copy data using cross-database queries on ra3 instances
- Add schema DDL to extract
- Add user grants to extract
- Add view DDL to extract
- Add external table DDL to extract
- Add options to customize which tables/schemas are exported
- Format logging a bit better
- Export the generated DDL as a file


Feel free to make pull requests or issues!

Building a Release:
```
python3 -m build --wheel .
twine upload -r pypi dist/*
```
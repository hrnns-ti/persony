import os
import oracledb

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = oracledb.create_pool(
            user = os.getenv('ORACLE_USER'),
            password = os.getenv('ORACLE_PASSWORD'),
            dsn = os.getenv('ORACLE_DSN'),
            min = int(os.getenv('ORACLE_MIN_CONN', 1)),
            max = int(os.getenv('ORACLE_MAX_CONN', 5)),
            increment = 1,
        )
    return _pool

def get_connection():
    return get_pool().acquire()
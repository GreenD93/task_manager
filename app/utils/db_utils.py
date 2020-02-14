import pymysql
from utils.settings import *

def get_db_connection(
        host=CLOUD_SQL_HOST,
        port=CLOUD_SQL_PORT,
        user=CLOUD_SQL_USERNAME,
        passwd=CLOUD_SQL_PASSWD,
        db=CLOUD_SQL_SCHEMA_NAME,
        charset=CLOUD_SQL_CHARSET
):

    db = pymysql.connect(
        host=host,
        port=port,
        user=user,
        passwd=passwd,
        db=db,
        charset=charset
    )

    return db
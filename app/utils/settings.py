import os

# MYSQL INFO
CLOUD_SQL_HOST = '34.85.112.219'
CLOUD_SQL_PORT = 3306
CLOUD_SQL_USERNAME = 'vai'
CLOUD_SQL_PASSWD = 'wakdlsem'
CLOUD_SQL_SCHEMA_NAME = 'vai_db'  # schema name
CLOUD_SQL_CHARSET = 'utf8mb4'

REVIEW_URL = 'http://stg.sat.wemakeprice.com/review/attach/'

# crawling param
LABEL = {
        'shoes' : 2,
        'inte' : 6,
        'pet' : 31,
        'kitc' : 41
        }

#-------------------------------------
# file path

def get_working_dir():
    return os.getcwd()

CURRENT_WORKING_DIR = get_working_dir()
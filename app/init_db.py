import sys
import traceback

from utils.settings import *
from utils.db_utils import *

def create_tables():
    print('create_tables.......')

    try:
        db = get_db_connection()

        with db.cursor() as curs:

            sql = """
                CREATE TABLE IF NOT EXISTS test (
                    reviewId INT(10) NOT NULL,
                    message TEXT NULL,
                    image_url VARCHAR(50) NOT NULL,
                    score INT(1) NOT NULL,
                    label CHAR(6) NOT NULL,
                    err1 TINYINT(1) DEFAULT -1,
                    err2 TINYINT(1) DEFAULT -1,
                    seq INT(11), 
                    PRIMARY KEY(reviewId)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """

            curs.execute(sql)
            db.commit()

            # drop table
            if '-drop' in sys.argv:
                print('>> drop')

                # vai_products
                sql = "DROP TABLE IF EXISTS test;"
                curs.execute(sql)
                db.commit()

    except:
        traceback.print_exc()
        print('fail')

    finally:
        if db is not None:
            db.close()

if "__main__" == __name__:
    create_tables()
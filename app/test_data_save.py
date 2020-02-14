import pymysql

from utils.settings import *
from utils.db_utils import *


USE_PHASE_COMMIT = True
USE_EACH_COMMIT = False


#------------------------------------------------------
# EtlDataSaver

class EtlDataSaver():

    #---------------------------------------------
    # constructor
    def __init__(self, each_commit=USE_EACH_COMMIT):

        self.count = 0
        self.each_commit = each_commit
        self.phase_commit = not each_commit

        pass

    def save_items(self, items):

        db = get_db_connection()

        with db.cursor() as curs:

            curs.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
            db.commit()

            self._save_items(db, curs, items)

            db.commit()

    def _save_items(self, db, curs, arr_data):
        count = len(arr_data)

        if count == 0:
            return

        try:
            for data in arr_data:

                reviewId = int(data['reviewId'])
                message = data['message']

                image_url = data['image_url']
                score = int(data['score'])

                label = data['label']
                err1 = int(data['err1'])
                err2 = int(data['err2'])

                # ----------------------------------------
                # insert vai_products item
                self._insert_vai_test_item(
                    db, curs,
                    reviewId, message,
                    image_url, score,
                    label, err1,
                    err2
                    )

        except Exception as e:
            print('error')
            print(arr_data)
            raise e


    def _insert_vai_test_item(self, db, curs,
                                 reviewId, message,
                                 image_url, score,
                                 label, err1, err2):

        sql = """
            INSERT INTO test (
                reviewId, message,
                image_url, score,
                label, err1,
                err2
            )
            VALUES (
                %s, %s,
                %s, %s,
                %s, %s,
                %s
            );
        """

        sql_args = (
            reviewId, message,
            image_url, score,
            label, err1,
            err2
        )

        curs.execute(sql, sql_args)

        if self.each_commit:
            db.commit()

        pass

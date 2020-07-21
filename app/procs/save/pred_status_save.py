# coding: utf-8

from pprint import pprint

from utils.util import *
from utils.settings import *
from utils.db_utils import *

USE_PHASE_COMMIT = True
USE_EACH_COMMIT = False


#------------------------------------------------------
# ImageStatusSaver

class ImageStatusSaver():

    #---------------------------------------------
    # constructor
    def __init__(self,
                 host, user, passwd, schema):

        self.host = host
        self.user = user
        self.passwd = passwd
        self.schema = schema

        pass


    #---------------------------------------------
    # finalize
    def finalize(self):

        pass


    #---------------------------------------------
    # save_items
    def save_items(self, items):

        db = get_db_connection(host=self.host, user=self.user, passwd=self.passwd, db=self.schema)

        try:
            with db.cursor() as curs:
                curs.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
                db.commit()
                self._save_items(db, curs, items)
        except:
            print('>>> db save error1')

        finally:
            if db is not None:
                db.close()

    def _save_items(self, db, curs, arr_data):
        count = len(arr_data)

        if count == 0:
            return

        sql = ''

        #------------------------------------------------------------
        try:
            for data in arr_data:

                reviewid = int(data['reviewid'])
                #pred = int(data['pred'])
                pred = 1

                sql = """
                    UPDATE
                        test
                    SET
                        pred={0}
                    WHERE
                        reviewid={1}
                    ;
                """.format(pred, reviewid)

                curs.execute(sql)
                db.commit()

        except:
            print('>>> db save error2')

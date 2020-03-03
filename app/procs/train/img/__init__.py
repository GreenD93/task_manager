# coding: utf-8

import os

from pprint import pprint
import sqlite3
import pymysql

from utils.util import *
from utils.settings import *
from utils.db_utils import *

USE_PHASE_COMMIT = True
USE_EACH_COMMIT = False

#------------------------------------------------------
# PredStatusSavor

class PredStatusSavor():

    #---------------------------------------------
    # constructor
    def __init__(self):

        pass


    #---------------------------------------------
    # finalize
    def finalize(self):

        pass

    # ---------------------------------------------
    # save_items
    def save_items(self, items):

        db = None

        try:
            db = get_db_connection()

            with db.cursor() as curs:

                curs.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
                db.commit()

                self._save_items(db, curs, items)

                if (not USE_EACH_COMMIT) and (not USE_PHASE_COMMIT):
                    db.commit()

        except:
            pprint('[ERROR] : save_items')

            pass

        finally:
            if db is not None:
                db.close()

        pass

    # ----------------------------------
    # _save_items
    def _save_items(self, db, curs, arr_data):

        count = len(arr_data)

        if count == 0:
            return

        sql = ''

        try:
            # ------------------------------------------------------------
            for data in arr_data:

                prod_id = int(data['prod_id'])
                item_type = int(data['item_type'])
                link_type = int(data['link_type'])

                sql = """
                    UPDATE
                        vai_checks
                    SET
                        changed=0
                    WHERE
                        prod_id=%s
                        AND link_type=%s
                        AND item_type=%s
                    ;
                """

                sql_args = (
                    prod_id, link_type, item_type,
                )

                curs.execute(sql, sql_args)

                if USE_EACH_COMMIT:
                    db.commit()

            # ------------------------------------------------------------
            if USE_PHASE_COMMIT and count > 0:
                db.commit()

        except Exception as e:
            s = sql + '\n' + get_exception_log()
            log_warn(s)
            log_warn(repr(sql_args))

            raise e

        pass

from utils.util import *
from utils.db_utils import *
from utils.settings import *

import sys


class DBCollector():

    # -------------------------------------
    # constructor
    def __init__(self,
                 host, user, passwd, schema, table, rows_per_page=100):

        self.host = host
        self.user = user
        self.passwd = passwd
        self.schema = schema

        self.table = table
        self.rows_per_page = rows_per_page

        pass

    def get_items(self):

        db = get_db_connection(host=self.host, user=self.user, passwd=self.passwd, db=self.schema)

        try:
            with db.cursor() as curs:
                curs.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
                db.commit()

                has_next = True

                last_seq = -1

                while has_next:

                    if last_seq == -1:
                        last_seq = sys.maxsize

                    str_seq_filter = 't.seq < {}'.format(last_seq)

                    sql = """
                        SELECT
                            t.seq,
                            t.reviewId,
                            t.image_url,
                            t.score,
                            t.label

                        FROM
                            {0} t
                            
                        WHERE
                            {1}

                        ORDER BY
                            t.seq DESC

                        LIMIT
                            {2};
                    """.format(
                        self.table,
                        str_seq_filter,
                        self.rows_per_page
                    )

                    curs.execute(sql)
                    rows = curs.fetchall()

                    item_count_in_page = len(rows)

                    if item_count_in_page < 50 or item_count_in_page == 0:
                        has_next = False

                    for row in rows:
                        item_count_in_page += 1

                        seq = row[0]
                        last_seq = seq

                        review_id = row[1]
                        image_url = row[2]
                        score = row[3]
                        label = row[4]

                        result = {
                            'seq': seq,
                            'reviewid': review_id,
                            'image_url': image_url,
                            'score': score,
                            'label': label
                        }

                        yield result

        except:
            print('db collect error')

        finally:
            if db is not None:
                db.close()

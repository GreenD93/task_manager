import sys

from utils.util import *
from utils.settings import *


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

    def _get_items_from_db(self):
        try:
            print(self.host, self.user, self.passwd, self.schema)
            db = get_db_connection(host=self.host, user=self.user, passwd=self.passwd, db=self.schema)

            with db.cursor() as curs:
                curs.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
                db.commit()

            has_next = True
            start_pos = 100

            while has_next:
                item_count_in_page = 0

                for item in self._get_rows(start_pos=start_pos, curs=curs):
                    item_count_in_page += 1

                    start_pos = min(item['seq'], start_pos)

                if item_count_in_page < 100 or item_count_in_page == 0:
                    has_next = False

    def _get_rows(self, start_pos, curs):

        sql = """
            SELECT
                t.seq
                t.reviewId,
                t.image_url,
                t.score

            FROM
                {0} as t
                
            WHERE
                t.seq < {1}
                
            ORDER BY 
                t.seq DESC
            LIMIT
                {2}
        """.format(
            self.table,
            start_pos,
            self.rows_per_page,
            curs)

        curs.execute(sql)
        rows = curs.fetchall()

        for row in rows:
            seq = row[0]
            review_id = row[1]
            image_url = row[2]
            score = row[3]

            result = {
                'seq': seq,
                'review_id': review_id,
                'image_url': image_url,
                'score': score
            }

            yield result










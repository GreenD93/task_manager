import sys
import os

import time

from utils.util import *
from utils.settings import *
from utils.db_utils import *

import urllib.request

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
                start_pos = sys.maxsize

                while has_next:

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
                            t.seq < {1}
                        ORDER BY
                            t.seq DESC

                        LIMIT
                            {2};
                    """.format(
                        self.table,
                        start_pos,
                        self.rows_per_page
                    )

                    curs.execute(sql)

                    rows = curs.fetchall()

                    item_count_in_page = len(rows)
                    if item_count_in_page < 100 or item_count_in_page == 0:
                        has_next = False

                    for row in rows:
                        item_count_in_page += 1

                        seq = row[0]
                        review_id = row[1]
                        image_url = row[2]
                        score = row[3]
                        label = row[4]

                        result = {
                            'seq': seq,
                            'review_id': review_id,
                            'image_url': image_url,
                            'score': score,
                            'label': label
                        }
                        start_pos = min(result['seq'], start_pos)

                        yield result

        except:
            print('db collect error')

        finally:
            if db is not None:
                db.close()





collector =  DBCollector(
            host="127.0.0.1",
            user="vai",
            passwd="wakdlsem",
            schema="vai_db",
            table="test",
            rows_per_page=100
        )


count = 0

for item in collector.get_items():
    img_name = item['image_url'].split('/')[1] + '.jpg'
    save_path = os.path.join('res/train_imgs', item['label'], img_name)

    download_url = REVIEW_URL + item['image_url']

    urllib.request.urlretrieve(download_url, save_path)
    count += 1

    if (count % 100) == 0:
        time.sleep(10)






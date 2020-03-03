# coding: utf-8
import os
import copy
import random
import sys

from pprint import pprint
import numpy as np
import pandas as pd

from pandas import DataFrame as df
from collections import defaultdict

from tensorflow.keras.preprocessing.image import ImageDataGenerator

from utils.util import *
from utils.settings import *
from utils.db_utils import *

from procs.train.train_settings import *

from procs.train.img.img_download import ImageDownloader


#------------------------------------------------------
# DatasetGenerator
class DatasetGenerator():

    #---------------------------------------------
    # constructor
    def __init__(self, max_sample_count, batch_size, img_width):

        # alphanumeric / dict -> utils에 추가하기!
        self.categories = list(CATEGORIES_DICT.keys())

        self.max_sample_count = max_sample_count
        self.batch_size = batch_size
        self.img_width = img_width

        self.raw_dataset = []
        self.dataframe = None

        self.data_generator = None

        pass


    #---------------------------------------------
    # get_data_generators
    def get_data_generators(self, trainable=True):

        image_size = (self.img_width, self.img_width)

        #--------------------------
        # 학습용 dataset generator

        #--------------------------
        # dataset 만들기
        self.raw_dataset, real_row_count_dict = self._collect_raw_dataset()
        pprint('>> dataset length: {}'.format(len(self.raw_dataset)))
        #ImageDownloader(self.img_width).download_train_imgs(self.raw_dataset)
        self._make_dataset()

        #--------------------------
        # generator 만들기
        self.data_generator = ImageDataGenerator(rescale=1./255, validation_split=0.2)

        train_data_generator = self.data_generator.flow_from_dataframe(
            dataframe=self.dataframe,
            directory=SAMPLE_IMGS_PATH,
            x_col = 'filename',
            y_col = 'category',
            target_size=image_size,
            color_mode='rgb',
            class_mode='sparse',
            batch_size=self.batch_size,
            subset="training"
        )

        val_data_generator = self.data_generator.flow_from_dataframe(
            dataframe=self.dataframe,
            directory=SAMPLE_IMGS_PATH,
            x_col = 'filename',
            y_col = 'category',
            target_size=image_size,
            color_mode='rgb',
            class_mode='sparse',
            batch_size=self.batch_size,
            subset="validation"
        )

        return train_data_generator, val_data_generator, real_row_count_dict, None


    #---------------------------------------------
    # get_row_count
    def get_row_count(self):
        return len(self.raw_dataset)


    #---------------------------------------------
    # _collect_raw_dataset
    def _collect_raw_dataset(self):
        pprint('>> _collect_raw_dataset')

        # default dict를 만들기
        categories_rows_dict = defaultdict(list)
        count_dict = defaultdict(int)

        # category 종류 사전에 define 하기
        categories = self.categories

        for category in categories:
            categories_rows_dict[category]
            count_dict[category] = 0

        for item in self._get_rows_from_db():

            n_categories = list(count_dict.values())
            criterion = list(map(lambda x : x  > self.max_sample_count, n_categories))

            # 샘플의 모든 category가 최대 개수 이상이면, 샘플 그만 모오기
            if all(criterion):
                break

            # item['category']로 추가해서 sudo 코드 작성
            category = item['label']

            # category별 sample 모으기
            if count_dict[category] > self.max_sample_count:
                continue
            else:
                count_dict[category] += 1
                self._append_sample(categories_rows_dict, item)

        real_row_count_dict = dict(count_dict)

        pprint('>> real categories_count: {}'.format(real_row_count_dict))

        #------------------------------
        # max_sample_count에서 모자란만큼 채우기
        # category 이름
        for category in self.categories:
            self._fill_rows(categories_rows_dict, category)

        #------------------------------
        # merge_sample
        raw_dataset = []

        filled_count_dict = defaultdict(int)
        for category in self.categories:
            filled_count_dict[category] = len(categories_rows_dict[category])

        for i in range(self.max_sample_count):
            for category in self.categories:
                if i < filled_count_dict[category]:
                    raw_dataset.append(categories_rows_dict[category][i])

        #------------------------------
        pprint('<< filled categories_count: {}'.format(filled_count_dict))

        return raw_dataset, real_row_count_dict


    #---------------------------------------------
    # _fill_rows
    def _fill_rows(self, categories_rows_dict, category):
        rows = categories_rows_dict[category]

        if len(rows) == 0:
            return

        prev_count = len(rows)

        if prev_count < self.max_sample_count:
            count = self.max_sample_count - prev_count
            row_count = len(rows)

            for _ in range(count):
                i = random.randint(0, row_count-1)
                cloned_row = copy.copy(rows[i])
                rows.append(cloned_row)

        pass


    #---------------------------------------------
    # _get_rows_from_db
    def _get_rows_from_db(self):

        db = None
        try:
            db = get_db_connection(host='127.0.0.1', user='vai',
                                   passwd='wakdlsem', db='vai_db')
            curs = db.cursor()

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
                        AND t.label in ('kitc', 'pet', 'shoes')
                        
                    ORDER BY
                        t.seq DESC

                    LIMIT
                        {2};
                """.format(
                    'test',
                    start_pos,
                    100
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

        except GeneratorExit:
            return

        except Exception as e:
            print('db_error')

        finally:
            if db is not None:
                db.close()


    #---------------------------------------------
    # _append_sample
    def _append_sample(self, categories_rows_dict, item):

        # [GCS path, y_val, LOCALFILE name]
        # LOCALFILE name = check_time.prod_id.jpg  (ex:  1576243899_254595322.jpg )


        #gcs_path = item['path']
        img_name = item['image_url'].split('/')[1] + '.jpg'
        gcs_path = os.path.join('train_imgs', item['label'], img_name)

        # x_val.replace('.jpg', '_{}.jpg'.format(item['check_time']))
        # local_path = '{}_{}'.format(item['check_time'], get_filename(gcs_path))
        # local_path = '{}_{}'.format('', get_filename(gcs_path))
        local_path = gcs_path

        # pprint(local_path)

        category = item['label']
        y_val = category

        categories_rows_dict[category].append([gcs_path, y_val, local_path])
        pass


    #---------------------------------------------
    # _make_dataset
    def _make_dataset(self):
        pprint('>> _make_dataset')

        x_vals = []
        y_vals = []

        for item in self.raw_dataset:
            filename = '{}/'.format(item[1]) + get_filename(item[2])
            y_val = str(item[1])

            # 만약 파일이 없다면, 앞의 배열에서 아무거나 한개 가져오기
            # if not os.path.exists('{}/{}'.format(SAMPLE_IMGS_PATH, filename)):
            #     i = random.randint(0, len(x_vals))
            #     print(x_vals)
            #     filename = x_vals[i]
            #     y_val = y_vals[i]

            x_vals.append(filename)
            y_vals.append(y_val)

        self.dataframe = df(data={'filename': x_vals, 'category': y_vals})
        print(self.dataframe)
        pass

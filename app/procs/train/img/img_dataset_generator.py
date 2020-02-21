# coding: utf-8

import copy
import random

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
        self.categoreis = list(CATEGORIES_DICT.keys())

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
        if trainable:

            #--------------------------
            # dataset 만들기
            self.raw_dataset, real_row_count_dict = self._collect_raw_dataset()
            log_info('>> dataset length: {}'.format(len(self.raw_dataset)))
            ImageDownloader(self.img_width).download_train_imgs(self.raw_dataset)
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


        #--------------------------
        # 테스트용 dataset generator
        else:
            #--------------------------
            # dataset 만들기
            self.raw_dataset, real_row_count_dict = self._collect_raw_dataset()
            ImageDownloader(self.img_width).download_train_imgs(self.raw_dataset)
            self._make_dataset()

            #--------------------------
            # generator 만들기
            self.data_generator = ImageDataGenerator(rescale=1./255)


            val_data_generator = self.data_generator.flow_from_dataframe(
                dataframe=self.dataframe,
                directory=SAMPLE_IMGS_PATH,
                x_col = 'filename',
                y_col = 'category',
                target_size=image_size,
                color_mode='rgb',
                class_mode='sparse',
                batch_size=self.batch_size
            )

            return val_data_generator, None, real_row_count_dict, None


    #---------------------------------------------
    # get_row_count
    def get_row_count(self):
        return len(self.raw_dataset)


    #---------------------------------------------
    # _collect_raw_dataset
    def _collect_raw_dataset(self):
        log_info('>> _collect_raw_dataset')

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
            category = item['category']

            # category별 sample 모으기
            if count_dict[category] > self.max_sample_count:
                continue
            else:
                count_dict[category] += 1
                self._append_sample(categories_rows_dict, item)

        real_row_count_dict = dict(count_dict)

        log_info('>> real categories_count: {}'.format(real_row_count_dict))

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
        log_info('<< filled categories_count: {}'.format(filled_count_dict))

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

            # log_note('>>1 count: {}'.format(count))
            # log_note('>>1 row_count: {}'.format(row_count))

            for _ in range(count):
                i = random.randint(0, row_count-1)
                cloned_row = copy.copy(rows[i])
                # categories_rows_dict[category].append(cloned_row)
                rows.append(cloned_row)

        pass


    #---------------------------------------------
    # _get_rows_from_db
    def _get_rows_from_db(self):
        result = None

        last_seq = -1
        has_more = True

        db = None
        try:
            db = get_db_connection()
            curs = db.cursor()

            curs.execute('SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED')
            db.commit()

            while has_more:

                if last_seq == -1:
                    str_seq_filter = ''
                else:
                    str_seq_filter = 'AND seq < {}'.format(last_seq)

                # category정보 추가

                sql = """
                    SELECT
                        seq,
                        prod_id,
                        item_type,
                        check_time,
                        is_ok,
                        category
                    FROM
                        vai_checks
                    WHERE
                        is_ok > -1
                        AND check_user_name != 'AUTO'
                        /*AND check_user_name != '윤빈'*/
                        {}
                    ORDER BY
                        seq DESC
                    LIMIT 1000
                """.format(str_seq_filter)

                # log_info(sql)

                curs.execute(sql)
                rows = curs.fetchall()

                count = 0
                for row in rows:

                    count += 1

                    if last_seq == -1:
                        last_seq = row[0]
                    else:
                        last_seq = min(last_seq, row[0])

                    prod_id = row[1]
                    item_type = row[2]
                    check_time = datetime_to_seconds(row[3])
                    category = row[5]

                    # is_ok = row[5]
                    # if is_ok == 0:
                    #     str_path = make_checked_img_url(prod_id, (item_type == ITEM_TYPE_WIDE))
                    # else:
                    #     str_path = row[6]

                    str_path = make_checked_img_url(prod_id, (item_type == ITEM_TYPE_WIDE))


                    result = {
                        'prod_id': prod_id,
                        'item_type': item_type,
                        'path': str_path,
                        'check_time': check_time,
                        'category' : category
                    }

                    yield result

                has_more = (count > 0)

        except GeneratorExit:
            return

        except Exception as e:
            logging.info(get_exception_log())

        finally:
            if db is not None:
                db.close()


    #---------------------------------------------
    # _append_sample
    def _append_sample(self, categories_rows_dict, item):

        # [GCS path, y_val, LOCALFILE name]
        # LOCALFILE name = check_time.prod_id.jpg  (ex:  1576243899_254595322.jpg )

        gcs_path = item['path']
        # x_val.replace('.jpg', '_{}.jpg'.format(item['check_time']))
        local_path = '{}_{}'.format(item['check_time'], get_filename(gcs_path))

        # log_info(local_path)

        category = item['category']
        y_val = category

        categories_rows_dict[category].append([gcs_path, y_val, local_path])
        pass


    #---------------------------------------------
    # _make_dataset
    def _make_dataset(self):
        log_info('>> _make_dataset')

        x_vals = []
        y_vals = []

        for item in self.raw_dataset:
            filename = get_filename(item[2])
            y_val = str(item[1])

            # 만약 파일이 없다면, 앞의 배열에서 아무거나 한개 가져오기
            if not os.path.exists('{}/{}'.format(SAMPLE_IMGS_PATH, filename)):
                i = random.randint(0, len(x_vals))
                filename = x_vals[i]
                y_val = y_vals[i]

            x_vals.append(filename)
            y_vals.append(y_val)

        self.dataframe = df(data={'filename': x_vals, 'category': y_vals})

        pass

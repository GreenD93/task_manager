# coding: utf-8
import time
from pprint import pprint

from tasks.task import Task

import numpy as np

from utils.util import *
from utils.settings import *

from procs.train.img.img_batch_predict import ImageBatchPredictor


MAX_COLLECT_COUNT = 100

class TaskModelPredictor(Task):

    # ---------------------------------------------
    # constructor

    def __init__(self, params={}):
        super(TaskModelPredictor, self).__init__(params)
        self.model_name = get_json_value(params, 'model_name', 'no_model')
        self.predictor = None

    # -------------------------------------
    # init_self
    def init_self(self):
        self.predictor = ImageBatchPredictor(self.model_name)

        self.count.value = 0
        pass

    # -------------------------------------
    # run_self
    def run_self(self):

        count = 0
        items = []

        while count < MAX_COLLECT_COUNT:
            data = self.get_input_data()

            if data is not None:
                time.sleep(0.1)

                self.put_output_data(data)
                self.count.value += 1
                count += 1

        #-------------------------------------------
        # 배치로 처리할 대상이 있다면
        # if count > 0:
            # 배치로 prediction
            #result_items = self.predictor.batch_check_items(items)

            # 결과를 다음 큐로 푸시
            # for item in items:
            #     self.put_output_data(item)
            #     self.count.value+=1
        pass

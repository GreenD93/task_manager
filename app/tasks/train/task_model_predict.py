from pprint import pprint

from tasks.task import Task

import numpy as np

from utils.util import *
from utils.settings import *

from procs.train.img.img_batch_predict import ImageBatchPredictor

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
        pass

    def run_self(self):

        count = 0
        items = []

        while count < 9:
            data = self.get_input_data()
            if data is not None:
                items.append(data)
                count += 1
        #-------------------------------------------
        # 배치로 처리할 대상이 있다면
        if count > 0:

            # 배치로 prediction
            result_items = self.predictor.batch_check_items(items)

            # 결과를 다음 큐로 푸시
            for item in result_items:
                self.put_output_data(item)
        pass
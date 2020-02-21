from pprint import pprint

from tasks.task import Task

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
        # self.predictor = ImageBatchPredictor(self.model_name)
        pass

    def run_self(self):

        count = 0
        while count < 9:
            data = self.get_input_data()
            if data is not None:
                print('predict', data)
                count += 1
        pass
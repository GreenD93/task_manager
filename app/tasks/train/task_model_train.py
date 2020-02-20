from pprint import pprint

from tasks.task import Task

from utils.util import *
from utils.settings import *

from procs.train.img.img_model_handle import ImageModelHandler

#---------------------------------------------------
# TaskModelTrainer

class TaskModelTrainer(Task):

    #-------------------------------------
    # constructor
    def __init__(self, params={}):
        super(TaskModelTrainer, self).__init__(params)

        self.item_type = get_json_value(params, 'item_type', 'image')
        self.model_name = get_json_value(params, 'model_name', 'mo_model')
        self.model = None

    #-------------------------------------
    # init_self
    def init_self(self):

        # image
        if self.item_type == 'image':
            self.model = ImageModelHandler(
                            name=self.model_name,
                            max_sample_count=self.max_sample_count,
                            batch_size=self.batch_size,
                            max_epoch_count=self.max_epoch_count,
                        )

    # -------------------------------------
    # run_self
    def run_self(self):
        if self.model is not None:
            self.model.train()

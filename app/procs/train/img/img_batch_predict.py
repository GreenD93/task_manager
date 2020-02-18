import numpy as np

from utils.util import *
from utils.settings import *

from procs.train.img.img_model_handle import ImageModelHandler

#---------------------------------------------------
# ImageBatchPredictor

class ImageBatchPredictor():

    #---------------------------------------------------
    # singleton

    g_instance = None

    @staticmethod
    def get_instance():
        if ImageBatchPredictor.g_instance is None:
            ImageBatchPredictor.g_instance = ImageBatchPredictor()

        return ImageBatchPredictor.g_instance

    #---------------------------------------------------
    # constructor
    def __init__(self, model_name):
        self.model_handler = ImageModelHandler(name=model_name)
        print(self.model_handler.name)
        pass

    #---------------------------------------
    # batch_check_items
    def batch_check_items(self, items):
        self.model_handler.predict(items)
        pass

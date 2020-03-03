# coding: utf-8

import os

import logging
import warnings

import numpy as np

from utils.util import *
from utils.settings import *

from procs.train.img.img_model_handle import ImageModelHandler

_LIMIT_VALUE_ = 0.5

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

        pass

    #---------------------------------------
    # batch_check_items
    def batch_check_items(self, items):

        arr_img = [item['img'] for item in items]

        preds = self.model_handler.predict(arr_img)

        if preds is not None:

            for i in range(preds.shape[0]):

                item = items[i]
                item['pred'] = preds[i]

        return items
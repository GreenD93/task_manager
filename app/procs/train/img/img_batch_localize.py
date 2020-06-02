# coding: utf-8

import tensorflow as tf
import tensorflow_hub as tf
from PIL import Image

import os
import logging
import warnings

import numpy as np

from utils.util import *
from utils.settings import *

from procs.train.train_settings import *
#---------------------------------------------------
# ImageBatchLocalizer

class ImageBatchLocalizer():

    #---------------------------------------------------
    # singleton
    g_instance = None

    @staticmethod
    def get_instance():
        if ImageBatchLocalizer.g_instance is None:
            ImageBatchLocalizer.g_instance = ImageBatchLocalizer()

        return ImageBatchLocalizer.g_instance

    #---------------------------------------------------
    # constructor
    def __init__(self):
        # path
        self.localizer = hub.load('path')
        pass

    #---------------------------------------
    # batch_localize_items
    def batch_localize_items(self, items):
        arr_img = [self._resize_img(item['img']) for item in items]
        arr_img = tf.image.convert_image_dtype(arr_img, dtype=tf.float32)

        preds = self.localizer.signatures['default'](arr_img)

        detection_boxes = preds['detection_boxes']
        detection_scroes = preds['detection_scores']

        for item, detection_box, detection_score in zip(items, detection_boxes, detection_scroes):
            criterion = detection_score > CLS_SCORE
            bboxes = detection_box[criterion]

            item['bbox'] = bboxes

        return items

    #---------------------------------------
    # _resize_img for object localization
    def _resize_img(self, img):

        # convert PIL format
        img = Image.fromarray(np.uint8(img))

        # img normalization
        resize_img = img.resize((192, 192))
        np_img = np.array(resize_img)/255

        return np_img
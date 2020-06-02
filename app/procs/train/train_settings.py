# coding: utf-8

from utils.settings import *

#---------------
# 경로관련
SAMPLE_IMGS_PATH = '{}/res/train_imgs'.format(CURRENT_WORKING_DIR)
MODEL_PATH = '{}/data/res/models/model.json'.format(CURRENT_WORKING_DIR)
MODEL_WEIGHTS_PATH = '{}/data/res/models/model.h5'.format(CURRENT_WORKING_DIR)

#---------------
# for IMAGE
N_CLASS = 3
IMG_WIDTH = 224
MAX_SAMPLE_COUNT = 1500 #3000 #1000 #2000 #3000 # 3000
BATCH_SIZE = 16 #8 #16 #864 #768 #512 #256 #64 #16 #16 # 64 32 8 10  64
MAX_EPOCH_COUNT = 5 #100 #100

CATEGORIES_DICT = {
    'kitc' : 0,
    'pet' : 1,
    'shoes' : 2
}

CLS_SCORE = 0.6
import asyncio
import os
import numpy as np

from PIL import Image

import urllib
import urllib.request
from io import BytesIO

from utils.util import *
from utils.db_utils import *
from utils.settings import *


class ImageLoader():

    # -------------------------------------
    # constructor
    def __init__(self):
        pass

    def temp_load_img(self, item):
        img_path = os.path.join('res/train_imgs', item['label'], item['image_url'].split('/')[1]+'.jpg')
        im_src = Image.open(img_path)

        im = im_src.convert('RGB')

        np_img = np.array(im, dtype=np.uint8)
        item['img'] = np_img

    def load_img(self, item):
        np_img = self._fetch(item)
        item['img'] = np_img

    # --------------------------
    # fetch
    def _fetch(sess, item):
        img_url = item['image_url']

        src_img_url = REVIEW_URL + img_url

        byte = urllib.request.urlopen(src_img_url).read()
        im_src = Image.open(BytesIO(byte))

        im = im_src.convert('RGB')

        np_img = np.array(im, dtype=np.uint8)

        return np_img
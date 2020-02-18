import asyncio

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

    def load_imgs(self, items):
        for item in items:
            np_img = self._fetch(item)
            item['img'] = np_img

        # ------------------------------------------
        # 신규이미지 읽어오기 (async)
        # if len(items) > 0:
        #     asyncio.run(self._load_imgs_async(items)

    # async def _load_imgs_async(self, items):
    #
    #     #--------------------------
        # fetch
    def _fetch(sess, item):
        img_url = item['image_url']

        src_img_url = REVIEW_URL + img_url

        byte = urllib.request.urlopen(src_img_url).read()
        im_src = Image.open(BytesIO(byte))

        im = im_src.convert('RGB')

        np_img = np.array(im, dtype=np.uint8)

        return np_img



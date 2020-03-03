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
      print('url'*50)
      # print(item['image_url'].split('/')[1]+'.jpg')
      # img_path = os.path.join('res/train_imgs', item['category'])
      # im_src = Image.open(img_path)
      #
      # im = im_src.convert('RGB')
      #
      # np_img = np.array(im, dtype=np.uint8)
      # item['img'] = np_img
      pass


  def load_img(self, item):

      np_img = self._fetch(item)
      item['img'] = np_img

      pass
      # ------------------------------------------
      # 신규이미지 읽어오기 (async)
      # if len(items) > 0:
      #     asyncio.run(self._load_imgs_async(items)

  # async def _load_imgs_async(self, items):

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

item = {
    'image_url' : 'http://stg.sat.wemakeprice.com/review/attach/' + '46972363/1535407526006/450x0.jpg'
}

IL = ImageLoader()

IL.load_img(item)

print(item)

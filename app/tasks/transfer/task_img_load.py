# coding: utf-8
import time

from tasks.task import Task

from utils.util import *
from utils.settings import *

from procs.transfer.img_load import ImageLoader

class TaskImgLoader(Task):
    #---------------------------------------------
    # constructor
    def __init__(self, params={}):
        super(TaskImgLoader, self).__init__(params)

        self.loader = None

    #-------------------------------------
    # init_self
    def init_self(self):
        self.loader = ImageLoader()
        pass

    def run_self(self):
        items = []
        while len(items) < 10:
            data = self.get_input_data()
            image_url = data['image_url']

            self.loader.get_urls(image_url)

            items.append(data)



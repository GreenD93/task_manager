# coding: utf-8
import time

from tasks.task import Task

from utils.util import *
from utils.settings import *

from procs.transfer.img_load import ImageLoader

#---------------------------------------------------
# TaskImgLoader
MAX_COLLECT_TIME = 1
MAX_COLLECT_COUNT = 100

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

        self.count.value = 0
        pass

    def run_self(self):

        count = 0
        items = []
        start_t = time.time()
        delta_t = 0

        while (delta_t < MAX_COLLECT_TIME) and (count < MAX_COLLECT_COUNT):

            data = self.get_input_data()

            if data is not None:
                time.sleep(1)
                items.append(data)
                count += 1

            delta_t = time.time() - start_t

        #-------------------------------------------
        # 배치로 처리할 대상이 있다면
        if count > 0:
            #결과를 다음 큐로 푸시
            for item in items:
                self.put_output_data(item)

            self.count.value += count

# coding: utf-8

from pprint import pprint

from time import sleep
from datetime import datetime

from tasks.task import Task

from utils.util import *
from utils.settings import *

from procs.train.img_batch_localize import ImageBatchLocalizer

MAX_COLLECT_TIME = 5
MAX_COLLECT_COUNT = 16 #16 #100 #200 #10000 # 100

#---------------------------------------------------
# TaskModelLocalizer

class TaskModelLocalizer(Task):

    #-------------------------------------
    # constructor
    def __init__(self, params={}):

        super(TaskModelLocalizer, self).__init__(params)
        # self.bypass = get_json_value(params, 'bypass', False)
        self.out_buf_hold_limit = get_json_value(params, 'out_buf_hold_limit', 200)
        self.use_only_manual = get_json_value(params, 'use_only_manual', True)

        self.localizer = None
        pass


    #-------------------------------------
    # init_self
    def init_self(self):
        self.localizer = ImageBatchLocalizer()
        self.count.value = 0
        pass


    #-------------------------------------
    # run_self
    def run_self(self):

        if self.out_buffer_full():
            sleep(0.2)
            return

        try:
            count = 0
            items = []

            start_t = time.time()
            delta_t = 0

            #-------------------------------------------
            # 배치로 처리할 아이템을 모은다
            while (delta_t < MAX_COLLECT_TIME) and (count < MAX_COLLECT_COUNT):

                data = self.get_input_data()
                if data is not None:
                    items.append(data)
                    count += 1

                else:
                    sleep(0.005)

                delta_t = time.time() - start_t

            #-------------------------------------------
            # 배치로 처리할 대상이 있다면
            if count > 0:

                # 배치로 prediction
                result_items = items
                # if not self.bypass:
                #     result_items = self.predictor.batch_check_items(items)
                result_items = self.localizer.batch_localize_items(items)

                # 결과를 다음 큐로 푸시
                for item in result_items:
                    self.put_output_data(item)

                self.count.value += count

        except Exception as e:
            log_warn(get_exception_log())


    #-------------------------------------
    # done_self
    def done_self(self):
        self.model = None
        pass


    #-------------------------------------
    # out_buffer_full
    def out_buffer_full(self):

        # 출력버퍼에 2만개 이상 있는지 여부 확인
        if (self.q_out is not None) and (self.q_out.qsize() > self.out_buf_hold_limit):  # 20000
            return True

        return False

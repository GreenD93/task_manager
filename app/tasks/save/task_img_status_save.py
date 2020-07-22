# coding: utf-8
import time

from utils.util import *
from utils.settings import *

from tasks.task import Task
from procs.save.pred_status_save import ImageStatusSaver

#---------------------------------------------------
# TaskImageStatusSaver

MAX_COLLECT_COUNT = 400

class TaskImageStatusSaver(Task):

    #---------------------------------------------
    # constructor
    def __init__(self, params={}):
        # Task.__init__(self, params)
        super(TaskImageStatusSaver, self).__init__(params)

        self.host = get_json_value(params, 'host', '')
        self.user = get_json_value(params, 'user', '')
        self.passwd = get_json_value(params, 'passwd', '')
        self.schema = get_json_value(params, 'schema', '')

        self.status_saver = None

    #---------------------------------------------
    # init_self
    def init_self(self):
        self.status_saver = ImageStatusSaver(
            self.host,
            self.user,
            self.passwd,
            self.schema
        )

        pass

    #---------------------------------------------
    # run_self
    def run_self(self):
        count = 0
        items = []

        while count < MAX_COLLECT_COUNT:
            data = self.get_input_data()
            if data is not None:
                items.append(data)
                count += 1

        #-------------------------------------------
        # 배치로 처리할 대상이 있다면
        if count > 0:
            self.status_saver.save_items(items)
        pass

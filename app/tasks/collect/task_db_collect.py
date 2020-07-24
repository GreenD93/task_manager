# coding: utf-8
import time

from tasks.task import Task

from utils.util import *
from utils.settings import *

from procs.transfer.db_collect import DBCollector

MAX_COLLECT_COUNT = 100

class TaskDBCollecter(Task):
    #---------------------------------------------
    # constructor
    def __init__(self, params={}):
        super(TaskDBCollecter, self).__init__(params)

        #actor
        self.actor = get_json_value(params, 'actor', 'none')

        self.host = get_json_value(params, 'host', '')
        self.user = get_json_value(params, 'user', '')
        self.passwd = get_json_value(params, 'passwd', '')
        self.schema = get_json_value(params, 'schema', '')

        self.table = get_json_value(params, 'table', '')
        self.rows_per_page = get_json_value(params, 'rows_per_page', 50)

        self.max_limit = get_json_value(params, 'max_limit', 100)

        self.collector = None

    #-------------------------------------
    # init_self
    def init_self(self):
        self.collector = DBCollector(
            self.host,
            self.user,
            self.passwd,
            self.schema,

            self.table,
            self.max_limit,
            self.rows_per_page
        )

        self.count.value = 0

        pass

    #---------------------------------------------
    # run_self
    def run_self(self):

        item_count = 0

        for item in self.collector.get_items():

            if item_count >= self.max_limit:
                self.pause_event.set()
                break

            # 만약 중지상태이면, 리턴
            if self.can_pause_or_stop():
                break

            time.sleep(0.1)
            self.put_output_data(item)
            self.count.value += 1
            item_count += 1

    def done_self(self):
        pass

    #-------------------------------------
    # can_pause_or_stop
    def can_pause_or_stop(self):
        return self.pause_event.is_set() or self.stop_event.is_set()

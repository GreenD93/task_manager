# coding: utf-8
import time

from tasks.task import Task

from utils.util import *
from utils.settings import *

from procs.transfer.db_collect import DBCollector


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
            self.rows_per_page
        )

        pass

    def run_self(self):
        for item in self.collector.get_items():
            self.put_output_data(item)
            print('collect',item)

    def done_self(self):
        pass
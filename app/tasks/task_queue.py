# coding: utf-8

from multiprocessing import Queue
from utils.util import *

class TaskQueue():

    instance_count = 0

    def __init__(self, params={}):
        self.q = Queue()
        TaskQueue.instance_count += 1

        self.name = get_json_value(params, 'name', None)
        self.stop_order = get_json_value(params, 'stop_order', 0)

        pass

    def start(self):
        self.q.close()
        self.q.join_thread()
        pass

    def stop(self):
        self.q.close()
        pass

    def get(self, block=True):
        return self.q.get(block, timeout=None)

    def put(self, data, block=True, timeout=None):
        return self.q.put(data, block, timeout)
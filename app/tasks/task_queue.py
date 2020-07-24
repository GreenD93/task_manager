# coding: utf-8
import multiprocessing
from tasks.task_custom_queue import Queue

from utils.util import *

class TaskQueue(object):

    instance_count = 0

    def __init__(self, params={}):
        self.q = Queue()
        TaskQueue.instance_count += 1

        self.name = get_json_value(params, 'name', None)
        self.stop_order = get_json_value(params, 'stop_order', 0)


        if self.name is None:
            self.name = 'queue_{:0d}'.format(TaskQueue.instance_count)

    def start(self):
        log_info('TaskQueue.start')
        # 백그라운드로 큐가 돌게함
        self.q.close()
        self.q.join_thread()


    def stop(self):
        self.q.close()
        pass

    def get(self, block=True, timeout=None):
        return self.q.get(block, timeout)

    def put(self, data, block=True, timeout=None):
        return self.q.put(data, block, timeout)

    def empty(self):

        result = False

        try:
            result = self.q.empty()

        except:
            result = True

        return result

    def qsize(self):
        return self.q.qsize()

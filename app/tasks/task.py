# coding: utf-8

import os
import psutil

from multiprocessing import Process
from multiprocessing import Event
import time

from utils.util import *


class Task(Process):

    instance_count = 0

    # ---------------------------------------------
    # constructor
    def __init__(self, params={}):
        # task_manager에서 객체로 queue를 객체로 받아옴

        super(Task, self).__init__()

        Task.instance_count += 1

        actor = get_json_value(params, 'actor', 'None')
        name = get_json_value(params, 'name', None)

        if name is None:
            name = 'task_{:0d}'.format(Task.instance_count)

        self.name = name

        self.container_idx = get_json_value(params, 'container_idx', 0)
        self.instance_id = get_json_value(params, 'instance_id', 0)

        self.actor = actor

        self.instance_count = get_json_value(params, 'instance_count', 1)

        self.q_in = get_json_value(params, 'q_in', None)
        self.q_out = get_json_value(params, 'q_out', None)

        self.pause_event = Event()
        self.stop_event = Event()
        self.busy_event = Event()

        self.st_time = 0

        self.count = get_json_value(params, 'processed_count', 1)

        pass

    #-------------------------------------
    # pause
    def pause(self):
        self.pause_event.set()
        pass

    #-------------------------------------
    # resume
    def resume(self):
        self.pause_event.clear()
        pass

    #-------------------------------------
    # stop
    def stop(self):
        self.stop_event.set()
        pass

    #-------------------------------------
    # is_stopped
    def is_stopped(self):
        return self.stop_event.is_set()

    #-------------------------------------
    # is_paused
    def is_paused(self):
        return self.pause_event.is_set()

    #-------------------------------------
    # set_busy
    def set_busy(self, value):
        if value:
            self.busy_event.set()
        else:
            self.busy_event.clear()
        pass

    #-------------------------------------
    # is_busy
    def is_busy(self):
        return self.busy_event.is_set()

    #-------------------------------------
    # run
    def run(self):
        self.init_self()
        self.run_self()
        pass

    #-------------------------------------
    # run_self
    # 상속받는 class에서 다시 define
    def run_self(self):
        pass

    #-------------------------------------
    # put_output_data
    def put_output_data(self, data):
        if self.q_out is not None:
            self.q_out.put(data)

        pass

    #-------------------------------------
    # get_input_data
    def get_input_data(self):

        if self.q_in is not None:
            result = self.q_in.get()

        return result

    #-------------------------------------
    # get_stats
    def get_stats(self):

        result = {}

        m = 0
        cpu_percent = 0
        alive = self.is_alive()
        busy = self.is_busy()
        waiting = 0
        processed = 0
        et = 0

        p = psutil.Process(self.pid)
        m = p.memory_info()[0] / (1024*1024)
        cpu_percent = p.cpu_percent(interval=0.1)

        # cpu_percent = p.cpu_percent()
        waiting = 0 if (self.q_in is None) else self.q_in.qsize()

        processed = self.count.value

        et = 0 if (self.st_time == 0) else self.get_lap_time()


        result = {
            'name': self.name,
            'pid': self.pid,
            'mem': int(m),
            'alive': alive,
            'busy': busy,
            'paused': self.is_paused(),
            'waiting': waiting,
            'processed': processed,
            'elapsed': et,
            'cpu': cpu_percent,
        }

        return result

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

        self.wait_secs_on_queue = get_json_value(params, 'wait_secs_on_queue', 0.25)

        self.pause_event = Event()
        self.stop_event = Event()
        self.busy_event = Event()

        self.st_time = 0
        self.is_first_data = True

        self.count = get_json_value(params, 'processed_count', 1)

        pass

    #-------------------------------------
    # pause
    def pause(self):
        print('Task.pause: {}'.format(self.name))
        self.pause_event.set()
        pass

    #-------------------------------------
    # resume
    def resume(self):
        if self.pause_event.is_set():
            self.st_time = time.time()
            print('Task.resume: {}'.format(self.name))
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
    # check_lap_time
    def check_lap_time(self):
        if self.st_time == 0:
            self.st_time = time.time()
        pass

    #-------------------------------------
    # init_lap_time
    def init_lap_time(self):
        self.st_time = 0
        pass

    #-------------------------------------
    # get_lap_time
    def get_lap_time(self):
        return time.time() - self.st_time

    #-------------------------------------
    # run
    def run(self):

        self.set_busy(True)

        print('Task.run:{}'.format(self.name))

        self.init_self()

        t = lap_time('[{}] Task.run - ready: paused[{}]'.format(self.name, self.pause_event.is_set()))


        # stop 이벤트가 발생할때까지 반복
        while not self.stop_event.is_set():

            if self.pause_event.is_set():

                self.init_lap_time()
                self.pause_self()
                print('[PAUSED] {} : sleeping'.format(self.name))
                time.sleep(self.wait_secs_on_queue)

            # 만약 실행상태이면
            else:

                self.check_lap_time()

                if (self.q_in is not None) and (self.q_in.empty()):
                    time.sleep(self.wait_secs_on_queue)
                    self.set_busy(False)

                else:
                    self.run_self()
                    self.set_busy(False)

        self.set_busy(False)

        t = lap_time('[{}] Task.run - end'.format(self.name), t)

        pass

    #-------------------------------------
    # run_self
    # 상속받는 class에서 다시 define
    def run_self(self):
        pass

    #-------------------------------------
    # pause_self
    def pause_self(self):
        pass

    #-------------------------------------
    # done_self
    def done_self(self):
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

        result = None

        if self.q_in is not None:

            if self.q_in.qsize():

                result = self.q_in.get()

                if result is not None:
                    self.set_busy(True)

            else:
                self.set_busy(True)

        if self.is_first_data:
            self.init_lap_time()
            self.is_first_data = False


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

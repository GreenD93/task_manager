from multiprocessing import Process
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

        self.actor = actor

        self.instance_count = get_json_value(params, 'instance_count', 2)

        self.q_in = get_json_value(params, 'q_in', None)
        self.q_out = get_json_value(params, 'q_out', None)

        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def stop(self):
        pass

    def run(self):
        self.init_self()
        self.run_self()
        pass

    # 상속받는 class에서 다시 define
    def run_self(self):
        pass

    # -------------------------------------
    # put_output_data
    def put_output_data(self, data):

        if self.q_out is not None:
            self.q_out.put(data)

        pass

    # -------------------------------------
    # get_input_data
    def get_input_data(self):

        if self.q_in is not None:
            result = self.q_in.get()

        return result
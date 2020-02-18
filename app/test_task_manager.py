import json
import importlib

from utils.settings import *
from utils.db_utils import *
from utils.util import *

from tasks.task_queue import TaskQueue


class TaskManager():

    # ---------------------------------------------
    # constructor
    def __init__(self):
        self.tasks = {}
        self.queues = {}
        self.arr_queues = []

        self.type_table = {}

        pass

    def load_tasks_from_profile(self, file_path):
        json_profile = file_to_json(file_path)

        # load queues
        self.load_queues(json_profile)

        # load tasks
        self.load_tasks(json_profile)

        # -------------------------------------
        # TASK READY 상태

        # task 준비

        for name, task in self.tasks.items():
            task.start()

        # queue 준비

        for name, queue in self.queues.items():
            queue.start()

        # -------------------------------------
        # TASK 종료 대기

        for name, task in self.tasks.items():
            task.join()

    def load_queues(self, json_profile):

        for k, json_queue in json_profile['queues'].items():

            q = TaskQueue({
                'name': k,
                'stop_order': json_queue['stop_order']
            })

            self.add_queue(q)

        self.arr_queues = list(sorted(self.arr_queues, key=lambda x: x.stop_order))

    def load_tasks(self, json_profile):

        # active task 확인
        active_tasks_name = json_profile['commons']['active_tasks']

        active_tasks = json_profile[active_tasks_name]

        # get task params
        for name, json_task in active_tasks.items():

            actor = get_json_value(json_task, 'actor', 'None')

            str_task_type = get_json_value(json_task, 'type', '')

            instance_count = get_json_value(json_task, 'instance_count', 1)
            str_q_in = get_json_value(json_task, 'q_in', '')
            str_q_out = get_json_value(json_task, 'q_out', '')

            q_in = self.get_queue(str_q_in)
            q_out = self.get_queue(str_q_out)

            params = {}

            params['instance_count'] = instance_count
            params['q_in'] = q_in
            params['q_out'] = q_out
            params['actor'] = actor

            # params
            for k, v in json_task['params'].items():
                params[k] = v

            _class = self.load_class(str_task_type)

            print(params)
            task = _class(params)

            self.add_task(task)

    # load task
    def load_class(self, str_type_path):

        # instance type
        p = str_type_path.rfind('.')
        module_path = str_type_path[0:p]
        type_name = str_type_path[p + 1:]

        _type = None

        # 만약 없으면 로딩
        if not str_type_path in self.type_table:
            module = importlib.import_module(module_path)

            _type = getattr(module, type_name)

            self.type_table[str_type_path] = _type

        # 만약 기존로딩된 것이 있으면, 그것을 반환
        else:
            _type = self.type_table[str_type_path]

        return _type

    # multi processing(append)
    def add_task(self, task):

        ## param
        self.tasks[task.actor] = task
        pass

    def add_queue(self, queue):
        self.queues[queue.name] = queue
        self.arr_queues.append(queue)

    def get_queue(self, name):
        if name in self.queues:
            return self.queues[name]
        else:
            return None


file_path = './profiles/task_profile.json'
file_to_json(file_path)
tm = TaskManager()

tm.load_tasks_from_profile(file_path)

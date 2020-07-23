import json
import importlib
import time
import enum
from multiprocessing import Value

from pprint import pprint
from io import StringIO

from utils.settings import *
from utils.db_utils import *
from utils.util import *

from tasks.task_queue import TaskQueue

class Status(enum.Enum):
    INIT                    = 0
    LOADING                 = 1
    LOADED                  = 2
    READY                   = 3
    RUNNING                 = 4
    STOPPING                = 5
    STOPPED                 = 6
    FORCE_STOP_OR_PAUSE      = 99

# watchdog을 매번 부를 시간간격
WATCHDOG_INTERVAL = 10

# 종료조건시에 각 진행마다 슬립시간
WATCHDOG_SLEEP_ON_STOPPING = 5

class TaskManager():

    ##########################################
    # singleton

    g_instance = None

    @staticmethod
    def get_instance():
        if TaskManager.g_instance is None:
            TaskManager.g_instance = TaskManager()

        return TaskManager.g_instance

    # ---------------------------------------------
    # constructor
    def __init__(self):
        self.tasks = {}
        self.queues = {}
        self.arr_queues = []

        self.type_table = {}

        self.tasks_status = Status.INIT

        self.container_idx = 0

        self.active_tasks_name = ''
        self.current_tasks_name = ''

        self.counters = dict()

        self.start_time = 0
        self.load_time = 0

        self.total_processed = 0

        pass

    #----------------------------------------------
    # select_next_container
    def select_next_container(self):
        self.container_idx += 1

    #----------------------------------------------
    # load_tasks_from_profile
    def load_tasks_from_profile(self, file_path):

        self.load_time = time.time()

        # -------------------------------------
        # INIT(STOP) 상태
        self.tasks_status = Status.INIT

        # TODO : while문으로 바꾸기

        # status loading
        self.tasks_status = Status.LOADING

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

        # status ready
        self.tasks_status = Status.READY

        # -------------------------------------
        # RUNNING 상태
        for name, task in self.tasks.items():
            task.resume()

        self.start_time = time.time()

        # status running
        self.tasks_status = Status.RUNNING

        # -------------------------------------
        # TASK 종료 대기
        for name, task in self.tasks.items():
            task.join()

        self.calculate_total_processed_counts()

        # 상태변수 클리어
        self.tasks.clear()
        self.queues.clear()
        self.arr_queues[:] = []

        # 반복문으로 계속 되는 부분
        # 다음 container로 넘어가기

        self.select_next_container()

    #----------------------------------------------
    # load_queues
    def load_queues(self, json_profile):

        for k, json_queue in json_profile['queues'].items():

            q = TaskQueue({
                'name': k,
                'stop_order': json_queue['stop_order']
            })

            self.add_queue(q)

        self.arr_queues = list(sorted(self.arr_queues, key=lambda x: x.stop_order))

    #----------------------------------------------
    # load_tasks
    def load_tasks(self, json_profile):

        if self.active_tasks_name == '':
            self.active_tasks_name = json_profile['commons']['active_tasks']

        #------------------------------------------------------
        # 현재 turn에서 스케줄된 테스크 찾기
        active_tasks = None

        if 'schedule' in json_profile['commons']:
            schedule = json_profile['commons']['schedule']

            if schedule['enabled']:
                for tasks in schedule['tasks']:
                    tasks_name = tasks[0]
                    tasks_width = tasks[1]
                    tasks_idx = tasks[2]
                    tasks_enabled = tasks[3]

                    # tasks 순서 정하는 mechanism
                    if tasks_enabled and ((self.container_idx % tasks_width) == tasks_idx):
                        active_tasks = json_profile[tasks_name]
                        self.current_tasks_name = tasks_name
                        break

        #------------------------------------------------------
        # 만약 현재 turn에서 스케줄된 테스크가 없으면, active_tasks_name을 이용하기
        if active_tasks is None:
            active_tasks = json_profile[self.active_tasks_name]
            self.current_tasks_name = self.active_tasks_name

        pprint(active_tasks)

        # get task params
        for name, json_task in active_tasks.items():

            actor = get_json_value(json_task, 'actor', 'None')

            str_task_type = get_json_value(json_task, 'type', '')

            instance_count = get_json_value(json_task, 'instance_count', 1)
            str_q_in = get_json_value(json_task, 'q_in', '')
            str_q_out = get_json_value(json_task, 'q_out', '')

            q_in = self.get_queue(str_q_in)
            q_out = self.get_queue(str_q_out)

            for i in range(instance_count):

                # params
                params = {}
                for k, v in json_task['params'].items():
                    params[k] = v

                params['container_idx'] = self.container_idx
                params['type_id'] = name
                params['name'] = '{}_{:02d}'.format(name, i)
                params['instance_id'] = i
                params['instance_count'] = instance_count
                params['q_in'] = q_in
                params['q_out'] = q_out

                counter_id = '{}_{:02d}'.format(name, i)
                if not (counter_id in self.counters):
                    self.counters[counter_id] = Value('i', 0)

                params['processed_count'] = self.counters[counter_id]

                # params
                for k, v in json_task['params'].items():
                    params[k] = v

                _class = self.load_class(str_task_type)

                task = _class(params)

                self.add_task(task)

    #----------------------------------------------
    # load_class
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

    #----------------------------------------------
    # add_task
    def add_task(self, task):
        ## param
        self.tasks[task.name] = task
        pass

    #----------------------------------------------
    # add_queue
    def add_queue(self, queue):
        self.queues[queue.name] = queue
        self.arr_queues.append(queue)

    #----------------------------------------------
    # get_queue
    def get_queue(self, name):
        if name in self.queues:
            return self.queues[name]
        else:
            return None

    #----------------------------------------------
    # print status
    def print_status(self):
        try:
            if len(self.tasks) > 0:
                print(self.get_status_strings())
        except:
            pass
        pass

    #----------------------------------------------
    # get_status_strings
    def get_status_strings(self):

        result = ''
        try:
            buf = StringIO()

            dt = time.time() - self.start_time
            dt_from_load = time.time() - self.load_time

            stats = self.get_stats()

            write_buf('', buf)
            write_buf('--------------------------------------------------------------------------------------------------', buf)
            write_buf('name            alive busy  paused     pid  cpu(%) mem(mb)   queue   cnt/s     sec   total', buf)
            write_buf('--------------------------------------------------------------------------------------------------', buf)

            max_processed = 0

            for stat in stats:

                processed = stat['processed']

                if processed is None:
                    processed = 0

                if processed > 0:
                    per_sec = dt / (processed + 0.000001)
                    per_sec = min(999999, per_sec)
                    per_count = processed / (dt + 0.000001)
                else:
                    per_sec = 0.0
                    per_count = 0.0

                alive = 'true  ' if stat['alive'] else 'false '
                busy = 'true  ' if stat['busy'] else 'false '
                paused = 'true  ' if stat['paused'] else 'false '

                cpu_f = int(stat['cpu'])
                if cpu_f == 0:
                    cpu = '{:8d}'.format(cpu_f)
                elif cpu_f > 100:
                    cpu = '{:8d}'.format(cpu_f)
                else:
                    cpu = '{:8d}'.format(cpu_f)

                waiting_count = stat['waiting']
                if waiting_count == 0:
                    waiting_count = '{:8,}'.format(waiting_count)
                else:
                    waiting_count = '{:8,}'.format(waiting_count)

                write_buf('{:16s}{}{}{}{:8d}{}{:8,}{}{:8.2f}{:8.4f}{:12,}'.format(
                    stat['name'],
                    alive,
                    busy,
                    paused,
                    stat['pid'],
                    cpu,
                    stat['mem'],
                    waiting_count,
                    per_count,
                    per_sec,
                    alive,
                    self.counters[stat['name']].value), buf)

                max_processed = max(max_processed, processed)

            write_buf('--------------------------------------------------------------------------------------------------', buf)

            write_buf(
                'STATUS:[{}]  COUNT: [{:,}]  ELAPSED: [{:.1f}] / [{:.1f}]'.format(
                    self.tasks_status,
                    (self.total_processed + max_processed),
                    dt,
                    dt_from_load,
                ), buf)

            write_buf('TASKS:[{}]   IDX:[{}]'.format(self.current_tasks_name, self.container_idx, ), buf)
            write_buf('--------------------------------------------------------------------------------------------------', buf)
            write_buf('', buf)

            result = buf.getvalue()

        except:
               pass

        return result

    #----------------------------------------------
    # calculate_total_processed_counts
    def calculate_total_processed_counts(self):
        count = 0

        for _, task in self.tasks.items():
            count = max(task.count.value, count)

        self.total_processed += count

        pass

    #----------------------------------------------
    # get_stats
    def get_stats(self):
        stats = []

        for name, task in self.tasks.items():
            stats.append(task.get_stats())

        stats = list(sorted(stats, key=lambda x: x['name']))

        self.last_stats = stats

        return stats


file_path = './profiles/task_profile.json'
file_to_json(file_path)
tm = TaskManager()

tm.load_tasks_from_profile(file_path)

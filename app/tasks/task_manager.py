# coding: utf-8
import json
import importlib
import time
import enum
from multiprocessing import Value

from threading import Thread

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
    FORCE_STOP_OR_PAUSE     = 99

# watchdog을 매번 부를 시간간격
WATCHDOG_INTERVAL = 5

# 종료조건시에 각 진행마다 슬립시간
WATCHDOG_SLEEP_ON_STOPPING = 2

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

        self.profile_loaded = False
        self.watch_dog_started = False

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
    # load_services
    def load_services(self, file_path):
        log_info('TaskManager.load')
        self.load_tasks_from_profile(file_path)
        self.start_watch_dog()
        pass

    #----------------------------------------------
    # pause_services
    def pause_services(self):

        log_info('TaskManager.pausing...')
        self.tasks_status = Status.FORCE_STOP_OR_PAUSE

        self.print_status()

        for name, task in self.tasks.items():
            task.pause()

        if len(self.tasks) > 0:
            time.sleep(10)

        self.print_status()

        log_info('TaskManager.paused')

        pass

    #----------------------------------------------
    # stop_services
    def stop_services(self):

        log_info('TaskManager.stopping...')
        self.tasks_status = Status.FORCE_STOP_OR_PAUSE

        #-------------------------------------
        # 일시멈춤
        self.pause_services()

        #---------------------------------------
        # 태스크/큐 미리 모아놓기
        arr_task = []
        for _, task in self.tasks.items():
            arr_task.append(task)

        arr_queue = []
        for _, queue in self.queues.items():
            arr_queue.append(queue)

        self.print_status()

        #-------------------------------------
        # 태스크 정지
        log_info('stopping tasks...')
        for task in arr_task:
            task.stop()

        #-------------------------------------
        # 큐 정지
        log_info('stopping queues...')
        for queue in arr_queue:
            queue.stop()

        self.print_status()

        #-------------------------------------
        for task in arr_task:
            log_info('task name:{}, pid:{}, alive:{}'.format(task.name, task.pid, task.is_alive()))

        for queue in arr_queue:
            log_info('queue name:{}, empty:{}'.format(queue.name, queue.empty()))

        self.print_status()

        log_info('TaskManager.stopped')
        pass

    #----------------------------------------------
    # load_tasks_from_profile
    def load_tasks_from_profile(self, file_path):

        self.load_time = time.time()

        #----------------------------------------------
        def _do_thread():

            # -------------------------------------
            # INIT(STOP) 상태
            self.tasks_status = Status.INIT

            while self.tasks_status != Status.FORCE_STOP_OR_PAUSE:

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

                # 만약 사용자가 태스크를 종료했다면
                if self.tasks_status == Status.FORCE_STOP_OR_PAUSE:
                    pass

                else:
                    self.tasks_status = Status.INIT
                    # 반복문으로 계속 되는 부분
                    # 다음 container로 넘어가기
                    self.select_next_container()

                    self.print_status()

                    time.sleep(5)

            if self.profile_loaded:
                log_info('>>> ALREADY PROFILE LOADED !!!')
                return

        self.profile_loaded = True
        th = Thread(target=_do_thread)
        th.start()

        pass


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

        log_note('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        log_note('>>> ACTIVE TASKS: {}'.format(self.active_tasks_name))
        log_note('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

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

        #pprint(active_tasks)

        # get task params
        for name, json_task in active_tasks.items():

            actor = get_json_value(json_task, 'actor', 'None')

            str_task_type = get_json_value(json_task, 'type', '')

            instance_count = get_json_value(json_task, 'instance_count', 1)

            is_loop = get_json_value(json_task, 'loop', True)

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
                params['loop'] = is_loop

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

                log_info('task: {}'.format(task))
                log_info('task q_in: {}'.format(task.q_in))
                log_info('task q_out: {}'.format(task.q_out))

            pass
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
    # start_watch_dog
    def start_watch_dog(self):

        #----------------------------------------------
        def _do_thread():

            while self.tasks_status != Status.FORCE_STOP_OR_PAUSE:

                time.sleep(WATCHDOG_INTERVAL)

                self.print_status()

                # 종료조건이면, 태스크 즉시종료
                if _is_done():

                    time.sleep(WATCHDOG_INTERVAL)

                    # 다시한번 종료조건 check
                    if _is_done():

                        log_note('>>> WATCHDOG STOPPING TASKS...')
                        self.tasks_status = Status.STOPPING

                        self.print_status()

                        _force_stop()

                        log_note('>>> WATCHDOG STOPPED TASKS.')
                        self.tasks_status = Status.STOPPED

                time.sleep(WATCHDOG_INTERVAL)


            log_info('>>> WATCHDOG EXITED !!!')

        def _is_done():

            # 아직 시작되지 않았으면, False
            if self.tasks_status != Status.RUNNING:
                return False

            # 큐에 데이터가 있으면, False
            for queue in self.arr_queues:
                if not queue.empty():
                    return False

            # task중 무언가가 처리중이면, False
            for name, task in self.tasks.items():
                if task.is_busy() and task.is_alive():
                    return False

            # 그렇지않다면, True
            return True

        def _force_stop():

            #---------------------------------------
            # 태스크/큐 미리 모아놓기
            arr_task = []
            for _, task in self.tasks.items():
                arr_task.append(task)

            arr_queue = []
            for _, queue in self.queues.items():
                arr_queue.append(queue)

            #---------------------------------------
            # 태스크 정지
            log_note('>> [WATCHDOG] STOPPING TASKS...')

            for task in arr_task:
                task.stop()

            if len(arr_task) > 0:
                time.sleep(WATCHDOG_SLEEP_ON_STOPPING)

            log_note('>> [WATCHDOG] STOPPED TASKS')

            #---------------------------------------
            # 큐 정지
            log_note('>> [WATCHDOG] STOPPING QUEUES...')
            for queue in arr_queue:
                queue.stop()

            if len(arr_queue) > 0:
                time.sleep(WATCHDOG_SLEEP_ON_STOPPING)

            log_note('>> [WATCHDOG] STOPPED QUEUES')

            pass

        if self.watch_dog_started:
            log_note('>>> WATCHDOG ALREADY RUNNING !!!')
            return

        self.watch_dog_started = True
        watch_dog_thread = Thread(target=_do_thread)
        watch_dog_thread.start()

        pass


    #----------------------------------------------
    # print status
    def print_status(self):
        try:
            if len(self.tasks) > 0:
                log_info(self.get_status_strings())
        except:
            pass
        pass

    #----------------------------------------------
    # get_status_strings
    def get_status_strings(self):

        result = ''

        buf = StringIO()

        dt = time.time() - self.start_time
        dt_from_load = time.time() - self.load_time

        stats = self.get_stats()

        write_buf('', buf)
        write_buf('--------------------------------------------------------------------------------------------------', buf)
        write_buf('name            alive busy  paused     pid  cpu(%) mem(mb)   queue   cnt/s     sec   total', buf)
        write_buf('--------------------------------------------------------------------------------------------------', buf)

        max_processed = 0

        for num, stat in enumerate(stats):

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

            alive = '$CYANtrue  $RESET' if stat['alive'] else '$MAGENTAfalse $RESET'
            busy = '$CYANtrue  $RESET' if stat['busy'] else '$MAGENTAfalse $RESET'
            paused = '$CYANtrue  $RESET' if stat['paused'] else '$MAGENTAfalse $RESET'

            cpu_f = int(stat['cpu'])
            if cpu_f == 0:
                cpu = '$MAGENTA{:8d}$RESET'.format(cpu_f)
            elif cpu_f > 100:
                cpu = '$YELLOW{:8d}$RESET'.format(cpu_f)
            else:
                cpu = '$CYAN{:8d}$RESET'.format(cpu_f)

            waiting_count = stat['waiting']
            if waiting_count == 0:
                waiting_count = '$MAGENTA{:8,}$RESET'.format(waiting_count)
            else:
                waiting_count = '$CYAN{:8,}$RESET'.format(waiting_count)


            write_buf('{:16s}{}{}{}{:8d}{}{:8,}{}$YELLOW{:8.2f}$RESET{:8.4f}{:12,}'.format(
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
                self.counters[stat['name']].value), buf)

            max_processed = max(max_processed, processed)

        write_buf('--------------------------------------------------------------------------------------------------', buf)

        write_buf(
            'STATUS:$BOLD$CYAN[{}]$RESET  COUNT: $YELLOW[{:,}]$RESET  ELAPSED:$BOLD$MAGENTA [{:.1f}]$RESET / $BOLD$GREEN[{:.1f}]$RESET'.format(
                self.tasks_status,
                (self.total_processed + max_processed),
                dt,
                dt_from_load,
            ), buf)

        write_buf('TASKS:$BOLD$GREEN[{}]$RESET   IDX:$BOLD$GREEN[{}]$RESET'.format(self.current_tasks_name, self.container_idx, ), buf)
        write_buf('--------------------------------------------------------------------------------------------------', buf)
        write_buf('', buf)

        result = buf.getvalue()

        return result

    #----------------------------------------------
    # get_stats
    def get_stats(self):
        stats = []

        for name, task in self.tasks.items():
            stats.append(task.get_stats())

        stats = list(sorted(stats, key=lambda x: x['name']))

        self.last_stats = stats

        return stats

    #----------------------------------------------
    # calculate_total_processed_counts
    def calculate_total_processed_counts(self):
        count = 0

        for _, task in self.tasks.items():
            count = max(task.count.value, count)

        self.total_processed += count

        pass

    #----------------------------------------------
    # get_pids
    def get_pids(self):
        pids = []

        for name, task in self.tasks.items():
            pids.append(task.pid)

        pids = list(sorted(pids))

        return pids

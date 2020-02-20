from utils.settings import *
from utils.db_utils import *
from utils.util import *
from pprint import pprint

file_path = './profiles/task_profile.json'
json_profile = file_to_json(file_path)

container_idx = 0

for i in range(0,50):
   if 'schedule' in json_profile['commons']:
      schedule = json_profile['commons']['schedule']
      if schedule['enabled']:
         for tasks in schedule['tasks']:
            tasks_name = tasks[0]
            tasks_width = tasks[1]
            tasks_idx = tasks[2]
            tasks_enabled = tasks[3]
   
            if tasks_enabled and ((container_idx % tasks_width) == tasks_idx):
               active_tasks = json_profile[tasks_name]
               pprint(active_tasks)

   container_idx += 1

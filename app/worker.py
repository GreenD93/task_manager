import os
import time
import psutil

import threading
import argparse

import requests

from tasks.task_manager import TaskManager

from utils.util import *
from utils.settings import *

from flask import Flask

port_no = 5000

app = Flask(__name__)

#----------------------------------------
# load
@app.route("/load")
def req_load_procs():
    TaskManager.get_instance().load_services('./profiles/task_profile.json')
    return "loading..."

#----------------------------------------
# pause
@app.route("/pause")
def req_pause_procs():
    TaskManager.get_instance().pause_services()
    return "pause"

#----------------------------------------
# stop
@app.route("/stop")
def req_stop_procs():
    TaskManager.get_instance().stop_services()
    return "stop"

#----------------------------------------
# starter
def start_runner():
    def start_loop():
        not_started = True
        while not_started:

            time.sleep(5)
            print('In start loop')

            r = requests.get('http://127.0.0.1:{}/load'.format(port_no))

            if r.status_code == 200:
                print('Server started, quiting start_loop')
                not_started = False
            print(r.status_code)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()


if __name__=='__main__':
    start_runner()
    app.run()

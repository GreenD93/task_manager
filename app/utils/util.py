import json
import os
import logging
import time

import pytz

from pprint import pprint
from datetime import datetime

def log_info(s):
    s = replace_log_tag(s)
    # log_info(s)

    logger = logging.getLogger("filelog")
    logger.info(s)

    pass

def get_json_value(jsonData, key, default_value):
    result = default_value

    if key in jsonData:
        result = jsonData[key]

    if result is None:
        result = default_value

    return result

def file_to_json(path):
    result = {}
    with open(path) as data_file:
        result = json.load(data_file)
    return result

def lap_time(msg, ct=None, log=True):
    t2 = time.time()
    t1 = t2 if ct is None else ct

    dt = t2 - t1

    if log:

        if dt == 0:
            print('## lap[{}]'.format(msg))
        else:
            print('## lap[{}]: {:.8f}'.format(msg, dt))

    return t2

############################################
# file utilities

def check_or_create_folder_from_filepath(file_path):
    folder = os.path.dirname(file_path)

    created = False

    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
            created = True
    except:
        pprint('making folder error')

    return folder, created

def json_to_file(path, json_data):
    with open(path, 'w') as data_file:
        json.dump(json_data, data_file, indent=2, sort_keys=True)
    pass

def json_to_str(json_obj, pretty=False):
    if pretty:
        return json.dumps(json_obj, indent=2, sort_keys=True)
    else:
        return json.dumps(json_obj)

def str_to_json(s):
    return json.loads(s)

def get_filename(file_path):
    return os.path.basename(file_path)

#---------------------------------------------
RESET_SEQ   = "\033[0m"
BOLD_SEQ    = "\033[1m"
RED_SEQ     = "\033[1;31m"
GREEN_SEQ   = "\033[1;32m"
YELLOW_SEQ   = "\033[1;33m"
BLUE_SEQ    = "\033[1;34m"
MAGENTA_SEQ = "\033[1;35m"
CYAN_SEQ    = "\033[1;36m"

def replace_log_tag(s):
    s = s.replace('$RESET', RESET_SEQ)
    s = s.replace('$BOLD', BOLD_SEQ)
    s = s.replace('$GREEN', GREEN_SEQ)
    s = s.replace('$YELLOW', YELLOW_SEQ)
    s = s.replace('$MAGENTA', MAGENTA_SEQ)
    s = s.replace('$CYAN', CYAN_SEQ)
    return s

#-------------------------------------
# write_buf
def write_buf(s, buf):
    buf.write(s + '\n')
    pass

##########################################
# time utilities

TIME_ZONE = None
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def _get_timezone():
    global TIME_ZONE

    if TIME_ZONE is None:
        TIME_ZONE = pytz.timezone('Asia/Seoul')
    return TIME_ZONE

def get_current_time_string(format_string=TIME_FORMAT):
    return datetime.now(_get_timezone()).strftime(format_string)

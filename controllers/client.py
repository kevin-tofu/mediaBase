
import os
import config
import time
import datetime
import uuid
from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
from database import client

def record(path, fname, test = None):

    data = {
        'path': path,
        'fname': fname,
        'id_data': str(uuid.uuid()),
        'datatime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        'uxtime': time.time()
    }

    if test is not None:
        return data

    client.insert_item(data)
    return data

def get_dataFrom_dataID(dataID):

    data = client.get_item_query({'dataID': dataID})
    return data

def get_dataFrom_id_data(id_data):

    data = client.get_item_query({'id_data': id_data})
    return data


def flush(test):

    if test is not None:
        return
    uxtime = time.time()
    datalist = client.get_all_items()

    for data_loop in datalist:

        if 'uxtime' in data_loop.keys():
            
            time_diff = uxtime - data_loop['uxtime']

            if config.DELETE_INTERVAL > 0:
                if time_diff > config.DELETE_INTERVAL:
                    
                    if 'path' in data_loop.keys() and 'fname' in data_loop.keys():
                        fpath = data_loop['path'] + data_loop['fname']
                        if os.path.exists(fpath) == True:
                            os.remove(fpath)
                    client.delete_item(data_loop['_id'])
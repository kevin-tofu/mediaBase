
import os
import time
import datetime
import uuid
# from zoneinfo import reset_tzpath

from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)

from mediaBase.database import mongo_client


class mongo_client_media(mongo_client):
    
    def __init__(self, _config):
        
        # super().__init__()
        # self.myclient = mongo_client(_config)
        
        super().__init__(_config)
        self.DELETE_INTERVAL = float(_config.DELETE_INTERVAL)

        # if True:
        if False:
            data = self.record("test", "test", "test", 'uuid', 0)
            _id = data['_id']
            result = self.delete_item(_id)
            print(_id, result)



    def record(self, 
               path, \
               fname_org, \
               fname, \
               _uuid, \
               status = 'created', \
               test = None):

        # uuid = str(uuid.uuid4())
        data = dict(
            path = path, \
            fname = fname, \
            fname_org = fname_org, \
            idData =  _uuid, \
            datatime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), \
            uxtime = time.time(), \
            status = status
        )
        print(data)

        # if test is not None or test == 0:
        # when it is testing, just return data without recording.
        if type(test) is int:
            if test != 0:
                return data
        elif test is not None:
            return data

        _id = self.insert_item(data)
        # print(_id, data)

        return data

    def get_status(self, idData):
        data = self.get_item_query({'idData': idData})
        return data['status']

    def get_dataFrom_dataID(self, dataID):

        data = self.get_item_query({'dataID': dataID})
        return data

    def get_dataFrom_idData(self, idData):

        data = self.get_item_query({'idData': idData})
        return data


    def flush(self, test):

        if test is not None:
            return
        
        uxtime = time.time()
        datalist = self.get_all_items()

        for data_loop in datalist:

            # logger.info(data_loop)
            if 'uxtime' in data_loop.keys():
                time_diff = uxtime - data_loop['uxtime']
                # logger.info("flush - time_diff")
                # logger.info(time_diff)
                if self.DELETE_INTERVAL > 0:
                    if time_diff > self.DELETE_INTERVAL:
                        
                        if 'path' in data_loop.keys() and 'fname' in data_loop.keys():
                            fpath = data_loop['path'] + data_loop['fname']
                            if os.path.exists(fpath) == True:
                                os.remove(fpath)
                                logger.info(f"removed - {fpath}")
                        self.delete_item(data_loop['_id'])

import os, sys
import config
from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
from fastapi.responses import FileResponse
from fastapi import HTTPException

import numpy as np
from PIL import Image
from io import BytesIO
import shutil

sys.path.append('./mediaBase/')
from controllers import client as myclient
from controllers import media_base
from controllers.utils import *

path_data = config.PATH_DATA
if os.path.exists(path_data) == False:
    os.makedirs(path_data)

class media_all(media_base.media_prod):
    
    def __init__(self):
        super().__init__()

    def draw_info2image(self, image, fpath_ex, **kwargs):
        raise NotImplementedError()
    
    def draw_info2video(self, fpath_org, fpath_ex, **kwargs):
        raise NotImplementedError()
        
    async def post_image_(self, file, **kwargs):
        
        logger.debug("post_image_")
        test = kwargs['test']

        myclient.flush(test)
        error_handling_image(file)
        fname = file.filename
        fname_ex = get_fname_image_key(fname)
        image = await read_save_image(path_data, fname, file, test)
        logger.info(fname)
        
        try:

            self.draw_info2image(f"{path_data}{fname}", f"{path_data}{fname_ex}", **kwargs)     
            # self.draw_info2image(image, path_data+fname_ex, **kwargs) 
            data_org = myclient.record(path_data, fname, test)
            data_ex = myclient.record(path_data, fname_ex, test)
                
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally:
            # if os.path.exists(f"{path_data}{fname}"):
            #     os.remove(f"{path_data}{fname}")
            #     logger.info(f"Deleted: {path_data}{fname}")
            pass

        return {'status': 'OK', 'idData': data_ex['idData']}

    async def post_video_(self, file, **kwargs):
        
        logger.info("post_video_")
        test = kwargs['test']
        myclient.flush(test)
        logger.info(f'{file.filename}, {file.content_type}')
        error_handling_video(file)
        
        try:
            fname = file.filename
            fname_ex = get_fname_video_key(fname)
            await save_video(path_data, fname, file, test)

            self.draw_info2video(path_data+fname, path_data+fname_ex, **kwargs)
            data_org = myclient.record(path_data, fname, test)
            data_ex = myclient.record(path_data, fname_ex, test)
                
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally: 
            pass

        return {'status': 'OK', 'idData': data_ex['idData']}


    def get_image_(self, idData, **kwargs):
        

        logger.info("get_image_")
        logger.info(f"idData: {idData}")
        if idData is None:
            raise HTTPException(status_code=400, detail="Value Error") 

        test = kwargs['test']
        if test == 1:
            path_export = path_data + "_test_image_prod.jpg"

        else:
            data = myclient.get_dataFrom_idData(idData)
            if 'fname' in data.keys():
                path_export = path_data + data['fname']
            else:
                raise HTTPException(status_code=400, detail='Error')

        logger.info(f'export: {path_export}')

        if os.path.exists(path_export) == True:
            return FileResponse(path_export)
        else:
            raise HTTPException(status_code=500, detail='Error')
            
            
    def get_video_(self, idData=None, **kwargs):
        
        logger.debug("get_video_")
        test = kwargs['test']
        print(idData)
        
        data = myclient.get_dataFrom_idData(idData)
        if 'fname' in data.keys():
            path_export = path_data + data['fname']
        else:
            raise HTTPException(status_code=400, detail='Error')
        
        logger.info(f'export: {path_export}')
        
        if os.path.exists(path_export) == True:
            return FileResponse(path_export, filename=path_export)
            # return FileResponse(path_export)
            # return {'status': 'ok'}
        else:
            raise HTTPException(status_code=500, detail='Error')

    async def post_video_info(self, file, **kwargs):
        
        logger.info("post_video_")
        test = kwargs['test']
        myclient.flush(test)
        logger.info(f'{file.filename}, {file.content_type}')
        error_handling_video(file)
        
        try:
            fname = file.filename
            fname_ex = get_fname_video_key(fname)
            await save_video(path_data, fname, file, test)

            result = self.getInfo_from_video(path_data+fname, path_data+fname_ex, **kwargs)
            # data_org = myclient.record(path_data, fname, test)
            # data_ex = myclient.record(path_data, fname_ex, test)
                
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally: 
            pass

        return result

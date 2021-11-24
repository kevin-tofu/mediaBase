
import os, sys
import config
from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
import json

from fastapi.responses import FileResponse, JSONResponse
#from fastapi import Request, File, UploadFile, HTTPException
from fastapi import HTTPException

import numpy as np
from skimage import io as sk_io
from PIL import Image
from io import BytesIO
import shutil

sys.path.append('./mediaBase/')
from controllers import client as myclient


path_data = config.PATH_DATA
if os.path.exists(path_data) == False:
    os.makedirs(path_data)


def error_handling_image_ext(ext_i):
    extention_image = ext_i in  ('jpg', 'jpeg', 'JPEG', 'png', 'PNG')
    if not extention_image:
        raise HTTPException(status_code=400, detail="The file is NOT .jpg or .jpeg")

def error_handling_video_ext(ext_v):
    extention_video = ext_v in ('mp4', 'MP4')
    if not extention_video:
        raise HTTPException(status_code=400, detail="The file is NOT 'mp4', 'MP4'")

def error_handling_image(file):
    error_handling_image_ext(file.filename.split('.')[-1])
def error_handling_video(file):
    error_handling_video_ext(file.filename.split('.')[-1])

def get_fname_image_key(fname):
    return fname.split('.')[0] + '_prod.jpg'
def get_fname_video_key(fname):
    return fname.split('.')[0] + '_prod.mp4'

async def read_image(file) -> Image.Image:

    logger.debug("read_imagefile")
    image = Image.open(BytesIO(await file.read()))
    return np.asarray(image)

async def save_image(_path, _fname, file, test):
    try:
        logger.info("save_image")
        image = Image.open(BytesIO(await file.read()))
        image.save(f"{_path}{_fname}")
        myclient.record(_path, _fname, test)
    except:
        raise HTTPException(status_code=400, detail='File Definition Error')

async def read_save_image(_path, _fname, _file, test):
    
    logger.info(f"save_image: {_path}{_fname}")
    try:
        ret = None
        image = Image.open(BytesIO(await _file.read()))
        image.save(f"{_path}{_fname}")
        ret = np.asarray(image)

    except:
        raise HTTPException(status_code=401, detail='File Definition Error')

    return ret


async def save_video(path, fname, file, test):

    logger.debug("save_video")
    try:
        with open(path + fname, 'wb') as local_temp_file:
            local_temp_file.write(file.file.read())
        myclient.record(path, fname, test)
    except:
        raise HTTPException(status_code=400, detail='File Definition Error')

class media_base():
    def __init__(self):
        pass

    def draw_info2image(self, image, fpath_ex, **kwargs):
        raise NotImplementedError()
    
    def draw_info2video(self, fpath_org, fpath_ex, **kwargs):
        raise NotImplementedError()
    
    def get_info_image(self, image, **kwargs):
        raise NotImplementedError()

    def get_info_video(self, fpath_org, **kwargs):
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

        self.draw_info2image(image, path_data+fname_ex, **kwargs) 
        try:
            

            data_org = myclient.record(path_data, fname, test)
            data_ex = myclient.record(path_data, fname_ex, test)
                
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 

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

        return {'status': 'OK', 'idData': data_ex['idData']}


    def get_image_(self, idData, **kwargs):
        

        logger.info("get_image_")
        logger.info(f"idData: {idData}")
        if idData is None:
            raise HTTPException(status_code=400, detail="Value Error") 

        test = kwargs['test']
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


    async def post_info_image_(self, file, **kwargs):

        logger.debug("post_coco_image_")
        logger.info(f'{file.filename}, {file.content_type}')
        test = kwargs['test']

        myclient.flush(test)

        error_handling_image(file)
        fname = file.filename
        image = await read_save_image(path_data, fname, file, test)

        fname_json = fname + '-image.json'

        try:
            # result = self.get_info_image(path_data+fname, **kwargs)
            result = self.get_info_image(f"{path_data}{fname}", **kwargs)
            
            logger.debug(result)
            with open(path_data + fname_json, 'w') as outfile:
                json.dump(result, outfile)
                myclient.record(path_data, fname_json, test)
            logger.info(f'saved: {path_data + fname_json}')
            
        except:
            raise HTTPException(status_code=503, detail="Error") 
        # finally:
        #     pass
        
        return result


    async def post_info_video_(self, file, **kwargs):

        logger.debug("post_coco_video")
        logger.info(f'{file.filename}, {file.content_type}')
        test = kwargs['test']
        
        error_handling_video(file)
        fname = file.filename
        fname_json = fname + '-video.json'
        await save_video(path_data, fname, file, test)
        
        try:
            result = self.get_info_video(f"{path_data}{fname}", **kwargs)
            logger.debug(result)
            with open(path_data + fname_json, 'w') as outfile:
                json.dump(result, outfile)
                myclient.record(path_data, fname_json, test)
            logger.info(f'saved: {path_data + fname_json}')
            
        except:
            raise HTTPException(status_code=503, detail="Error") 
        # finally:
        #     pass
        
        return result

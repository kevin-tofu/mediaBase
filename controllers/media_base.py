
import os
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
import mediapipe as mp
from format_annotation import fmt_coco

from mediapipe_if import parse
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

async def save_image(path, fname, file, test):
    try:
        logger.debug("save_image")
        image = Image.open(BytesIO(await file.read()))
        image.save(path + fname)
        myclient.record(path, fname, test)
    except:
        raise HTTPException(status_code=400, detail='File Definition Error')

async def read_save_image(_path, _fname, _file, test):
    
    logger.debug("save_image")
    try:
        ret = None
        image = Image.open(BytesIO(await _file.read()))
        image.save(_path + _fname)
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
        # from mediapipe_if.visualization import draw_keypoint2img
        # self.mp_pose = mp.solutions.pose
        # self.mp_drawing = mp.solutions.drawing_utils
        # self.mp_drawing_styles = mp.solutions.drawing_styles
        # parse.draw_keypoint2image(image, path_data+fname_ex,\
        #                              mp_pose, mp_drawing, mp_drawing_styles)
        # self.draw_keypoint2video(path_data+fname, path_data+fname_ex)
        # get_coco
        self.draw_keypoint2image = None
        self.draw_keypoint2video = None
        self.get_coco = None
        pass

    async def post_image_(self, file, test = None):
        
        logger.debug("post_image_")
        myclient.flush(test)

        error_handling_image(file)
        fname = file.filename
        fname_ex = get_fname_image_key(fname)
        image = await read_save_image(path_data, fname, file, test)
        
        logger.info(fname)
        try:
            self.draw_keypoint2image(image, path_data+fname_ex) 

            data_org = myclient.record(path_data, fname, test)
            data_ex = myclient.record(path_data, fname_ex, test)
                
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 

        return {'status': 'OK', 'id_data': data_ex['id_data']}

    async def post_video_(file, test = None):
        
        logger.debug("post_video_")
        myclient.flush(test)
        logger.info(f'{file.filename}, {file.content_type}')
        error_handling_video(file)
        
        try:
            fname = file.filename
            fname_ex = get_fname_video_key(fname)
            await save_video(path_data, fname, file, test)

            # parse.draw_keypoint2video(path_data+fname, path_data+fname_ex, mp_pose, mp_drawing, mp_drawing_styles)
            self.draw_keypoint2video(path_data+fname, path_data+fname_ex)
            data_org = myclient.record(path_data, fname, test)
            data_ex = myclient.record(path_data, fname_ex, test)
                
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 

        return {'status': 'OK', 'id_data': data_ex['id_data']}


    def get_image_(self, id_data=None, test=None):
        
        logger.debug("get_image_")
        print(id_data)
        
        data = myclient.get_dataFrom_id_data(id_data)
        if 'fname' in data.keys():
            path_export = path_data + data['fname']
        else:
            raise HTTPException(status_code=400, detail='Error')


        logger.info(f'export: {path_export}')

        if os.path.exists(path_export) == True:
            return FileResponse(path_export)
        else:
            raise HTTPException(status_code=500, detail='Error')
            
            
    def get_video_(self, id_data=None, test=None):
        
        logger.debug("get_video_")
        print(id_data)
        
        data = myclient.get_dataFrom_id_data(id_data)
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


    async def post_coco_image_(self, file, test):

        logger.debug("post_coco_image_")
        logger.info(f'{file.filename}, {file.content_type}')
        error_handling_image(file)
        fname = file.filename
        fname_json = fname + '-image.json'
        await save_image(path_data, fname, file, test)

        try:
            # coco_image, coco_annotations, coco_categories = \
            #     parse.get_cocokeypoint_from_image(path_data+fname, mp_pose)
            
            # result = {'images': coco_image,\
            #         'annotations': coco_annotations,\
            #         'annotations_bbox': [],\
            #         'categories': coco_categories,\
            #         'categories_bbox': [],\
            #         'info': fmt_coco.make_coco_info('original', '', url='', version='1.0'),\
            #         'licenses': [],\
            # }
            result = self.get_coco(path_data+fname)
            
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
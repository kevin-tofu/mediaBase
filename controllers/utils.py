import os
from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
from fastapi import HTTPException
import numpy as np
from PIL import Image
from io import BytesIO
import uuid

# sys.path.append('./mediaBase/')


def error_handling_image_ext(ext_i):
    extention_image = ext_i in  ('jpg', 'jpeg', 'JPEG', 'png', 'PNG')
    if not extention_image:
        raise HTTPException(status_code=400, detail="The file is NOT .jpg or .jpeg")

def error_handling_video_ext(ext_v):
    extention_video = ext_v in ('mp4', 'MP4')
    if not extention_video:
        raise HTTPException(status_code=400, detail="The file is NOT 'mp4', 'MP4'")

def get_fname_uuid(fname):

    myuuid = str(uuid.uuid4())
    fname_ext = os.path.splitext(fname)[-1]

    # print('fname', fname)
    # print('myuuid', myuuid)
    # print('fname_ext', fname_ext)

    fname_uuid = f"{myuuid}{fname_ext}"
    # print(fname_uuid)

    return fname_uuid, myuuid


def get_fname_prod(fname, ext=None):

    if ext is None:
        fname_ext = os.path.splitext(fname)[-1]
    elif type(ext) is str:
        fname_ext = ext
    else:
        fname_ext = ""

    fname_base = os.path.splitext(os.path.basename(fname))[0]
    fname_prod = f"{fname_base}-prod{fname_ext}"

    return fname_prod


def error_handling_image(file):
    error_handling_image_ext(file.filename.split('.')[-1])

def error_handling_video(file):
    error_handling_video_ext(file.filename.split('.')[-1])

async def read_image(file) -> Image.Image:

    logger.debug("read_imagefile")
    image = Image.open(BytesIO(await file.read()))
    return np.asarray(image)

async def save_image(_path, _fname, file, test):
    try:
        logger.info("save_image")
        image = Image.open(BytesIO(await file.read()))
        image.save(f"{_path}{_fname}")
        # myclient.record(_path, _fname, test)
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
        # myclient.record(path, fname, test)
    except:
        raise HTTPException(status_code=400, detail='File Definition Error')


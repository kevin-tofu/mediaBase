from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
from fastapi import HTTPException
import numpy as np
from PIL import Image
from io import BytesIO
# sys.path.append('./mediaBase/')


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


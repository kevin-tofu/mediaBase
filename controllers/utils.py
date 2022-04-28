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
    extention_image = ext_i in  ('jpg', 'jpeg', 'JPEG', 'png', 'PNG', 'JPG')
    if not extention_image:
        raise HTTPException(status_code=400, detail="The file is NOT 'jpg', 'jpeg', 'JPEG', 'png', 'PNG', 'JPG'")

def error_handling_video_ext(ext_v):
    extention_video = ext_v in ('mp4', 'MP4', 'AVI', 'avi', 'MOV', 'mov', 'wmv', 'WMV')
    if not extention_video:
        raise HTTPException(status_code=400, detail="The file is NOT mp4 or avi or mov or wmv")

def error_handling_json_ext(ext_i):
    extention_image = ext_i in  ('json')
    if not extention_image:
        raise HTTPException(status_code=400, detail="The file is NOT 'json'")

# def error_handling_video_ext(ext_v):
#     extention_video = ext_v in ('mp4', 'MP4')
#     if not extention_video:
#         raise HTTPException(status_code=400, detail="The file is NOT mp4")


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


def error_handling_json(file):
    error_handling_json_ext(file.filename.split('.')[-1])

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


def save_video(path, fname, file, test):

    logger.debug("save_video")
    try:
        with open(f"{path}/{fname}", 'wb') as local_temp_file:
            local_temp_file.write(file.file.read())
        # myclient.record(path, fname, test)
    except:
        raise HTTPException(status_code=400, detail='File Definition Error')


def convert2mp4(path_data, fname_src, fname_dst):

    import ffmpeg
    
    stream = ffmpeg.input(f"{path_data}{fname_src}", v="quiet")
    stream = ffmpeg.output(stream, f"{path_data}{fname_dst}", v="quiet")
    ffmpeg.run(stream)

def converter_xxx2mp4(path_data, fname):

    fname_noext = os.path.splitext(fname)[0]
    fname_dst = f'{fname_noext}.mp4'

    file_ext = os.path.splitext(fname)[-1]
    if file_ext == ".mp4" or file_ext == ".MP4":
        return fname
    else:
        convert2mp4(path_data, fname, fname_dst)
        if os.path.exists(f"{path_data}{fname}") == True:
            os.remove(f"{path_data}{fname}")

        return fname_dst

def set_audio(path_src, path_dst):
    """
    https://kp-ft.com/684
    https://stackoverflow.com/questions/46864915/python-add-audio-to-video-opencv
    """

    import os, shutil
    import moviepy.editor as mp
    import time

    root_ext_pair = os.path.splitext(path_src)
    path_dst_copy = f"{root_ext_pair[0]}-copy{root_ext_pair[1]}"
    shutil.copyfile(path_dst, path_dst_copy)
    time.sleep(0.5)

    # Extract audio from input video.                                                                     
    clip_input = mp.VideoFileClip(path_src)
    # clip_input.audio.write_audiofile(path_audio)
    # Add audio to output video.                                                                          
    clip = mp.VideoFileClip(path_dst_copy)
    clip.audio = clip_input.audio

    time.sleep(0.5)
    clip.write_videofile(path_dst)

    time.sleep(0.5)
    os.remove(path_dst_copy)


import os, sys
import config
from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
from fastapi.responses import FileResponse, JSONResponse
from fastapi import HTTPException
from mediaBase.controllers import utils

sys.path.append('./mediaBase/')
from controllers.utils import *

path_data = config.PATH_DATA
if os.path.exists(path_data) == False:
    os.makedirs(path_data)


class media_base():
    def __init__(self, _config):
        self.config = _config
    
    def get_info_2images(self, fpath_org1, fpath_org2, **kwargs):
        raise NotImplementedError()

    def get_info_image(self, fpath_org, **kwargs):
        raise NotImplementedError()

    def get_info_video(self, fpath_org, **kwargs):
        raise NotImplementedError()
    
    def post_anyfiles(self, files_list, **kwargs):
        raise NotImplementedError()


class media_prod(media_base):
    def __init__(self, _config):
        super().__init__(_config)

    def post_files(self, files_list, **kwargs):

        logger.debug("post_files")
        test = kwargs['test']

        for file in files_list:
            logger.info(f'{file.filename}, {file.content_type}')
        
        try:
        # if True:
            logger.debug("post_anyfiles")
            result = self.post_anyfiles(files_list, **kwargs)
            return result

        # try:
            # pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            # print("finally0")
            pass
            

    async def post_info_2images_(self, file1, file2, **kwargs):

        logger.debug("post_coco_image_")
        # print(kwargs)
        logger.info(f'{file1.filename}, {file1.content_type}')
        logger.info(f'{file2.filename}, {file1.content_type}')
        test = kwargs['test']
        fname2 = None
        fname1 = None

        error_handling_image(file1)
        error_handling_image(file2)

        try:
        # if True:
            fname1, uuid_f = utils.get_fname_uuid(file1.filename)
            image1 = await read_save_image(path_data, fname1, file1, test)
            fname2, uuid_f = utils.get_fname_uuid(file2.filename)
            image2 = await read_save_image(path_data, fname2, file2, test)
            # image = await read_image(file1)
            
            # fname_json = os.path.basename(fname1) + '-video.json'
            
            result = self.get_info_2images(f"{path_data}{fname1}", f"{path_data}{fname2}", **kwargs)
            
        # try:
            # pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            if os.path.exists(f"{path_data}{fname1}") and fname1 is not None:
                os.remove(f"{path_data}{fname1}")
                logger.info(f"Deleted: {path_data}{fname1}")
            if os.path.exists(f"{path_data}{fname2}") and fname1 is not None:
                os.remove(f"{path_data}{fname2}")
                logger.info(f"Deleted: {path_data}{fname2}")
            pass
        
        return result


    async def post_info_image_(self, file, **kwargs):

        logger.debug("post_coco_image_")
        logger.info(f'{file.filename}, {file.content_type}')
        test = kwargs['test']
        fname = None

        error_handling_image(file)

        try:

            fname, uuid_f = utils.get_fname_uuid(file.filename)
            image = await read_save_image(path_data, fname, file, test)
            # image = await read_image(path_data, fname, file, test)
            # fname_json = os.path.basename(fname) + '-video.json'
            
            result = self.get_info_image(f"{path_data}{fname}", **kwargs)
            # result = self.get_info_image(image, **kwargs)
            # logger.debug(result)
            # with open(path_data + fname_json, 'w') as outfile:
            #     json.dump(result, outfile)
            #     myclient.record(path_data, fname_json, test)
            # logger.info(f'saved: {path_data + fname_json}')

            pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            if os.path.exists(f"{path_data}{fname}") and fname is not None:
                os.remove(f"{path_data}{fname}")
                logger.info(f"Deleted: {path_data}{fname}")
        
        return result


    def post_info_video_(self, file, **kwargs):

        logger.debug("post_info_video_")
        logger.info(f'{file.filename}, {file.content_type}')
        test = kwargs['test']
        fname = None
        error_handling_video(file)

        try:
            
            fname, uuid_f = utils.get_fname_uuid(file.filename)
            save_video(path_data, fname, file, test)
            fname_json = os.path.basename(fname) + '-video.json'

            result = self.get_info_video(f"{path_data}{fname}", **kwargs)
            # logger.debug(result)
            # with open(path_data + fname_json, 'w') as outfile:
            #     json.dump(result, outfile)
            #     myclient.record(path_data, fname_json, test)
            # logger.info(f'saved: {path_data + fname_json}')

        # try:    
            # pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            if os.path.exists(f"{path_data}{fname}") and fname is not None:
                os.remove(f"{path_data}{fname}")
                logger.info(f"Deleted: {path_data}{fname}")
        
        return result


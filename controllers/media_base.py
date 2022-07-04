
import os, sys
import time
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

def remove_file(path_file: str, sleep_sec: int=30) -> None:

    # logger.info('timer')
    # time.sleep(sleep_sec)
    if os.path.exists(path_file) == True:
        os.unlink(path_file)
        logger.info(f'removed : {path_file}')

def remove_files(path_files: str, sleep_sec: int=30) -> None:

    # logger.info('timer')
    # time.sleep(sleep_sec)
    for path_file in path_files:
        if os.path.exists(path_file) == True:
            os.unlink(path_file)
            logger.info(f'removed : {path_file}')

class media_base():
    def __init__(self, _config):
        self.config = _config
        self.path_data = _config.PATH_DATA
        # self.sleep_sec_remove = _config.SLEEP_SEC_REMOVE
        # self.sleep_sec_remove_response = _config.SLEEP_SEC_REMOVE_RESPONSE

    def get_info_2images(self, fpath_org1, fpath_org2, **kwargs):
        raise NotImplementedError()

    def get_info_image(self, fpath_org, **kwargs):
        raise NotImplementedError()

    def get_info_video(self, fpath_org, **kwargs):
        raise NotImplementedError()
    
    def post_anyfiles(self, files_list, **kwargs):
        raise NotImplementedError()

    def xxx2mp4(self, fname):
        """
        """
        fname_noext = os.path.splitext(fname)[0]
        fname_dst = f'{fname_noext}.mp4'
        file_ext = os.path.splitext(fname)[-1]
        if file_ext == ".mp4" or file_ext == ".MP4":
            return fname
        else:
            # await self.convert2mp4(fname, fname_dst)
            utils.convert2mp4(self.path_data, fname, fname_dst)

            if os.path.exists(f"{self.path_data}{fname}") == True:
                os.remove(f"{self.path_data}{fname}")
            return fname_dst


    def process_anyfiles_fg(self, files_list, bgtask, **kwargs):
        raise NotImplementedError()


    def post_anyfiles_fg(self, files_list, bgtask, **kwargs):

        logger.info("post_anyfiles_fg")
        test = kwargs['test']

        try:
        # if True:

            path_files_list = list()
            for file in files_list:
                logger.info(f'{file.filename}, {file.content_type}')
                fname, uuid_f = utils.get_fname_uuid(file.filename)
                save_file(self.path_data, fname, file, test)
                path_files_list.append(f"{self.path_data}{fname}")
            
            result = self.process_anyfiles_fg(path_files_list, bgtask, **kwargs)

            bgtask.add_task(remove_files, path_files_list)
            # bgtask.add_task(remove_files, path_files_list, self.sleep_sec_remove)

            return result
        # try:
            # pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            # print("finally0")
            pass


    def post_image_fg(self, file, bgtask, **kwargs):
        """

            https://stackoverflow.com/questions/64716495/how-to-delete-the-file-after-a-return-fileresponsefile-path
        """

        logger.info("post_image_fg")
        test = kwargs['test']
        error_handling_image(file)

        try:
        # if True:
            fname_org = file.filename
            fname, uuid_f = get_fname_uuid(fname_org)
            save_file(self.path_data, fname, file, test)

            if "ext" in kwargs:
                fname_ex_org = get_fname_prod(fname, ext=kwargs['ext'])
            else:
                fname_ex_org = get_fname_prod(fname)
            
            _, uuid_ex = get_fname_uuid(fname_ex_org)
            logger.info(f"fname:{fname_ex_org}")
            
            kwargs["fname_org"] = fname_org
            kwargs['fgbg'] = 'fg'
            # logger.info(f'{fname}, {fname_ex_org}')
            self.draw_info2image(f"{self.path_data}{fname}", \
                                 f"{self.path_data}{fname_ex_org}", \
                                 **kwargs)
        
            # bgtask.add_task(remove_file, f"{self.path_data}{fname_ex_org}", self.sleep_sec_remove_response)
            bgtask.add_task(remove_file, f"{self.path_data}{fname}")
            bgtask.add_task(remove_file, f"{self.path_data}{fname_ex_org}")
            # if os.path.exists(f"{self.path_data}{fname_ex_org}") == True:

            _, ext = os.path.splitext(os.path.basename(fname_ex_org))
            return FileResponse(f"{self.path_data}{fname_ex_org}", \
                                # filename=f"{self.path_data}{fname_ex_org}", \
                                # filename=f"{fname_ex_org}", \
                                media_type = f'image/{ext[1::]}', \
                                background=bgtask)
            
            # _, image_enc = cv2.imencode('.png', image[:, :, ::-1])
            # return Response(content = image_enc.tostring(), media_type='image/png')

                # return FileResponse(f"{self.path_data}{fname_ex_org}", filename=f"{self.path_data}{fname_ex_org}")
            # else:
            #     raise Exception("Error") 
                
        # try:
            # pass
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally: 
            pass
            # if os.path.exists(f"{self.path_data}{fname}") == True:
            #     os.remove(f"{self.path_data}{fname}")

        

    def post_video_fg(self, file, bgtask, **kwargs):
        """

            https://stackoverflow.com/questions/64716495/how-to-delete-the-file-after-a-return-fileresponsefile-path
        """
        logger.info("post_video_fg")
        test = kwargs['test']
        error_handling_video(file)

        try:
        # if True:
            fname_org = file.filename
            fname, uuid_f = get_fname_uuid(fname_org)
            save_file(self.path_data, fname, file, test)

            fname = self.xxx2mp4(fname)
            if "ext" in kwargs:
                fname_ex_org = get_fname_prod(fname, ext=kwargs['ext'])
            else:
                fname_ex_org = get_fname_prod(fname)
            
            _, uuid_ex = get_fname_uuid(fname_ex_org)
            logger.info(f"fname:{fname_ex_org}")
            
            kwargs["fname_org"] = fname_org
            kwargs['fgbg'] = 'fg'
            # logger.info(f'{fname}, {fname_ex_org}')
            self.draw_info2video(f"{self.path_data}{fname}", \
                                 f"{self.path_data}{fname_ex_org}", \
                                 **kwargs)
        
            bgtask.add_task(remove_file, f"{self.path_data}{fname}")
            bgtask.add_task(remove_file, f"{self.path_data}{fname_ex_org}")
            # if os.path.exists(f"{self.path_data}{fname_ex_org}") == True:
            _, ext = os.path.splitext(os.path.basename(fname_ex_org))
            return FileResponse(f"{self.path_data}{fname_ex_org}", \
                                filename=f"{fname_ex_org}", \
                                # filename=f"{self.path_data}{fname_ex_org}", \
                                media_type = f'video/{ext[1::]}', \
                                background=bgtask)
            # else:
            #     raise Exception("Error") 

        # try:
            # pass
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally: 
            # if os.path.exists(f"{self.path_data}{fname}") == True:
            #     os.remove(f"{self.path_data}{fname}")
            pass

        

class media_prod(media_base):
    def __init__(self, _config):
        super().__init__(_config)

    
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
            
            kwargs["fname1_org"] = file1.filename
            kwargs["fname2_org"] = file2.filename
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
        # if True:

            fname, uuid_f = utils.get_fname_uuid(file.filename)
            image = await read_save_image(path_data, fname, file, test)
            
            kwargs["fname_org"] = file.filename
            result = self.get_info_image(f"{path_data}{fname}", **kwargs)
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
        # if True:
            
            fname, uuid_f = utils.get_fname_uuid(file.filename)
            save_file(path_data, fname, file, test)
            fname = self.xxx2mp4(fname)
            fname_json = os.path.basename(fname) + '-video.json'

            kwargs["fname_org"] = file.filename
            result = self.get_info_video(f"{path_data}{fname}", **kwargs)
        # try:    
            # pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            if os.path.exists(f"{path_data}{fname}") and fname is not None:
                os.remove(f"{path_data}{fname}")
                logger.info(f"Deleted: {path_data}{fname}")
        
        return result


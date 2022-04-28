
from email import utils
import os, sys
# import config
import numpy as np
from PIL import Image
from io import BytesIO
import shutil
from fastapi.responses import FileResponse
from fastapi import HTTPException


if __name__ != '__main__':
    from logconf import mylogger
    logger = mylogger(__name__)
    print('__name__', __name__)

    # sys.path.append('./mediaBase/')
    from mediaBase.controllers import client
    from mediaBase.controllers import media_base
    from mediaBase.controllers.utils import *

else:
    from test_logger import mylogger
    logger = mylogger(__name__)
    print('__name__', __name__)

    import client
    import media_base
    from utils import *



class media_all(media_base.media_prod):
    
    def __init__(self, _config):
        super().__init__(_config)

        self.myclient = client.mongo_client_media(_config)

        self.path_data = _config.PATH_DATA
        if os.path.exists(self.path_data) == False:
            os.makedirs(self.path_data)
    
    def draw_info2image_2images(self, fpath_org1, fpath_org2, fpath_ex, **kwargs):
        raise NotImplementedError()

    def draw_info2image(self, fpath_org, fpath_ex, **kwargs):
        raise NotImplementedError()
    
    def draw_info2video(self, fpath_org, fpath_ex, **kwargs):
        raise NotImplementedError()
    

    # async def convert2mp4(self, fname_src, fname_dst):

    #     import ffmpeg
    #     stream = ffmpeg.input(f"{self.path_data}{fname_src}", v="quiet")
    #     stream = ffmpeg.output(stream, f"{self.path_data}{fname_dst}", v="quiet")
    #     ffmpeg.run(stream)

    async def converter(self, fname):

        fname_noext = os.path.splitext(fname)[0]
        fname_dst = f'{fname_noext}.mp4'
        file_ext = os.path.splitext(fname)[-1]
        if file_ext == ".mp4" or file_ext == ".MP4":
            return fname
        else:
            # await self.convert2mp4(fname, fname_dst)
            await utils.convert2mp4(self.path_data, fname, fname_dst)

            if os.path.exists(f"{self.path_data}{fname}") == True:
                os.remove(f"{self.path_data}{fname}")
            return fname_dst

            
    async def post_2images_(self, file1, file2, **kwargs):
        
        logger.info("post_2images_")
        test = kwargs['test']

        self.myclient.flush(test)
        error_handling_image(file1)
        error_handling_image(file2)
        
        try:
        # if True:
            fname_org1 = file1.filename
            fname1, uuid_f1 = get_fname_uuid(fname_org1)
            fname_org2 = file2.filename
            fname2, uuid_f2 = get_fname_uuid(fname_org2)

            # fname_ex_org = get_fname_prod(fname)
            if "ext" in kwargs:
                # fname_ex_org1 = get_fname_prod(fname1, ext=kwargs['ext'])
                # fname_ex_org2 = get_fname_prod(fname2, ext=kwargs['ext'])
                fname_export, uuid_export = get_fname_uuid(fname1, ext=kwargs['ext'])
            else:
                fname_export, uuid_export = get_fname_uuid(fname1)
            
            # _, uuid_ex1 = get_fname_uuid(fname_ex_org1)
            # _, uuid_ex2 = get_fname_uuid(fname_ex_org2)
            await save_image(self.path_data, fname1, file1, test)
            await save_image(self.path_data, fname2, file2, test)

            # logger.info(f'{fname}, {fname_ex_org}')
            self.draw_info2image_2images(f"{self.path_data}{fname1}", \
                                         f"{self.path_data}{fname2}", \
                                         f"{self.path_data}{fname_export}", \
                                         **kwargs)

            data_org1 = self.myclient.record(self.path_data, fname_org1, fname1, uuid_f1, test)
            data_org2 = self.myclient.record(self.path_data, fname_org2, fname2, uuid_f2, test)
            data_ex = self.myclient.record(self.path_data, fname_export, fname_export, uuid_export, test)
            # print(data_ex)

        # try:
            # pass    
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally:

            if test is None:
                pass
            elif type(test) is int:
                if int(test) == 1:
                    if os.path.exists(f"{self.path_data}{fname1}"):
                        os.remove(f"{self.path_data}{fname1}")
                        logger.info(f"Deleted: {self.path_data}{fname1}")
                    if os.path.exists(f"{self.path_data}{fname2}"):
                        os.remove(f"{self.path_data}{fname2}")
                        logger.info(f"Deleted: {self.path_data}{fname2}")
                    if os.path.exists(f"{self.path_data}{fname_export}"):
                        os.remove(f"{self.path_data}{fname_export}")
                        logger.info(f"Deleted: {self.path_data}{fname_export}")

        return {'status': 'OK', 'idData': data_ex['idData']}


    async def post_image_(self, file, **kwargs):
        
        logger.info("post_image_")
        test = kwargs['test']

        self.myclient.flush(test)
        error_handling_image(file)
        
        try:
        # if True:
            fname_org = file.filename
            fname, uuid_f = get_fname_uuid(fname_org)
            # fname_ex_org = get_fname_prod(fname)
            if "ext" in kwargs:
                fname_ex_org = get_fname_prod(fname, ext=kwargs['ext'])
            else:
                fname_ex_org = get_fname_prod(fname)
            
            _, uuid_ex = get_fname_uuid(fname_ex_org)
            await save_image(self.path_data, fname, file, test)
            self.draw_info2image(f"{self.path_data}{fname}", 
                                 f"{self.path_data}{fname_ex_org}", 
                                 **kwargs)

            data_org = self.myclient.record(self.path_data, fname_org, fname, uuid_f, test)
            data_ex = self.myclient.record(self.path_data, fname_ex_org, fname_ex_org, uuid_ex, test)

        # try:
            # pass
        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally:
            # os.remove(f"{self.path_data}{fname}")
            # os.remove(f"{self.path_data}{fname_ex_org}")
            
            if test is None:
                pass
            elif type(test) is int:
                if int(test) == 1:
                    if os.path.exists(f"{self.path_data}{fname}") == True:
                        os.remove(f"{self.path_data}{fname}")
                    if os.path.exists(f"{self.path_data}{fname_ex_org}") == True:
                        os.remove(f"{self.path_data}{fname_ex_org}")
            else:
                raise ValueError("")                

        return {'status': 'OK', 'idData': data_ex['idData']}


        

    async def post_video_(self, file, **kwargs):
        
        logger.info("post_video_")
        test = kwargs['test']
        self.myclient.flush(test)
        # logger.info(f'{file.filename}, {file.content_type}')
        error_handling_video(file)

        # try:
        if True:
            fname_org = file.filename
            fname, uuid_f = get_fname_uuid(fname_org)
            await save_video(self.path_data, fname, file, test)

            fname = await self.converter(fname)
            # logger.info(f"fname:{fname}")

            # print(kwargs)
            if "ext" in kwargs:
                fname_ex_org = get_fname_prod(fname, ext=kwargs['ext'])
            else:
                fname_ex_org = get_fname_prod(fname)
            
            _, uuid_ex = get_fname_uuid(fname_ex_org)
            logger.info(f"fname:{fname_ex_org}")
            
            
            # logger.info(f'{fname}, {fname_ex_org}')
            self.draw_info2video(f"{self.path_data}{fname}", \
                                 f"{self.path_data}{fname_ex_org}", \
                                 **kwargs)

            
            logger.info(f"record: {fname}")
            data_org = self.myclient.record(self.path_data, fname_org, fname, uuid_f, test)

            logger.info(f"record: {fname_ex_org}")
            data_ex = self.myclient.record(self.path_data, fname_ex_org, fname_ex_org, uuid_ex, test)

        try:
            pass

        except:
            raise HTTPException(status_code=503, detail="Internal Error") 
        
        finally: 
            if test is None:
                pass
            
            elif type(test) is int:
                if int(test) == 1:
                    if os.path.exists(f"{self.path_data}{fname}") == True:
                        os.remove(f"{self.path_data}{fname}")
                    if os.path.exists(f"{self.path_data}{fname_ex_org}") == True:
                        os.remove(f"{self.path_data}{fname_ex_org}")
            else:
                raise ValueError("")

        return {'status': 'OK', 'idData': data_ex['idData']}


    def get_image_(self, idData, **kwargs):
        
        logger.info("get_image_")
        logger.info(f"idData: {idData}")
        if idData is None:
            raise HTTPException(status_code=400, detail="Value Error") 

        test = kwargs['test']
        # logger.info("test")
        # logger.info(test)
        if test == 1:
            path_export = f"{self.path_data}/test_image.jpg"
        else:
            data = self.myclient.get_dataFrom_idData(idData)
            if data is None:
                raise HTTPException(status_code=500, detail='The data is not found')

            if 'fname' in data.keys():
                path_export = f"{self.path_data}{data['fname']}"
            else:
                raise HTTPException(status_code=400, detail='Error')

        if os.path.exists(path_export) == True:
            return FileResponse(path_export)
        else:
            raise HTTPException(status_code=500, detail='Error')
            
            
    def get_video_(self, idData=None, **kwargs):
        
        logger.info("get_video_")
        logger.info(idData)
        if idData is None:
            raise HTTPException(status_code=400, detail="Value Error") 
        
        test = kwargs['test']
        if test == 1:
            path_export = f"{self.path_data}/test_video.mp4"
        else:
            data = self.myclient.get_dataFrom_idData(idData)
            if data is None:
                raise HTTPException(status_code=500, detail='The data is not found')
            
            if 'fname' in data.keys():
                path_export = f"{self.path_data}{data['fname']}"
            else:
                raise HTTPException(status_code=400, detail='Error')
        
        logger.info(f'export: {path_export}')
        if os.path.exists(path_export) == True:
            return FileResponse(path_export, filename=path_export)
        else:
            raise HTTPException(status_code=500, detail='Error')
        

if __name__ == '__main__':
    
    
    # import os
    # import sys
    # if __name__ == "__main__":
    # sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
    # import config as _config
    import test_config as _config

    fname_org = "name-org.jpg"
    test = None
    fname, uuid_f = get_fname_uuid(fname_org)
    fname_ex_org = get_fname_prod(fname)
    _, uuid_ex = get_fname_uuid(fname_ex_org)

    myclient = client.mongo_client_media(_config)
    data_ex = myclient.record(myclient.path_data, fname_ex_org, fname_ex_org, uuid_ex, test)



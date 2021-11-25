
import os, sys
import config
from logconf import mylogger
logger = mylogger(__name__)
print('__name__', __name__)
from fastapi.responses import FileResponse, JSONResponse
from fastapi import HTTPException
sys.path.append('./mediaBase/')
from controllers.utils import *

path_data = config.PATH_DATA
if os.path.exists(path_data) == False:
    os.makedirs(path_data)


class media_base():
    def __init__(self):
        pass
    
    def get_info_image(self, image, **kwargs):
        raise NotImplementedError()

    def get_info_video(self, fpath_org, **kwargs):
        raise NotImplementedError()
    

class media_prod(media_base):
    def __init__(self):
        super().__init__()


    async def post_info_image_(self, file, **kwargs):

        logger.debug("post_coco_image_")
        logger.info(f'{file.filename}, {file.content_type}')
        test = kwargs['test']

        # myclient.flush(test)

        error_handling_image(file)
        fname = file.filename
        image = await read_save_image(path_data, fname, file, test)
        fname_json = fname + '-image.json'
        
        try:
            # result = self.get_info_image(f"{path_data}{fname}", **kwargs)
            result = self.get_info_image(image, **kwargs)
            # logger.debug(result)
            # with open(path_data + fname_json, 'w') as outfile:
            #     json.dump(result, outfile)
            #     myclient.record(path_data, fname_json, test)
            # logger.info(f'saved: {path_data + fname_json}')
            pass
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            if os.path.exists(f"{path_data}{fname}"):
                os.remove(f"{path_data}{fname}")
                logger.info(f"Deleted: {path_data}{fname}")
        
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
            # logger.debug(result)
            # with open(path_data + fname_json, 'w') as outfile:
            #     json.dump(result, outfile)
            #     myclient.record(path_data, fname_json, test)
            # logger.info(f'saved: {path_data + fname_json}')
            
        except:
            raise HTTPException(status_code=503, detail="Error") 
        finally:
            if os.path.exists(f"{path_data}{fname}"):
                os.remove(f"{path_data}{fname}")
                logger.info(f"Deleted: {path_data}{fname}")
        
        return result


from .common import CommonArgs,CommonCmd,GeneralOptions

import logging

LOG = logging.getLogger(__name__)

import glob,os,tarfile
from datetime import datetime,timezone
class UploaderCmd(CommonCmd):
    
    def __init__(self, general:GeneralOptions ):
        super().__init__(general=general,args=None)
    
    def upload(self):
        LOG.info("uploading files to BBDD")
        path="data"
        if self.general.ccaa is not None:
            path+="/"+self.general.ccaa
            if self.general.short_name is not None:
                path+="/"+self.general.short_name

#        path="data/galicia/laopinioncoruna"
        repos = self.connectMongo()
        files=glob.glob(path+"/**/*", recursive=True)
        for file in files:
            if file.endswith(".tar"):
                LOG.debug(f"Reading: {file}")
                dir = os.path.dirname(file)
                group = os.path.basename(file).removesuffix(".tar")

                with tarfile.open(file, "r") as tar:
                    tar_files = tar.getnames()
                    for tar_file in tar_files:
                        info = tar.getmember(tar_file)
                        mtime = datetime.fromtimestamp(info.mtime, tz=timezone.utc)
                        sPath = dir+"/"+tar_file
                        #LOG.debug(f"Uploading [path: {sPath}, group: {group}, modDate:{mtime}]")
                        contents = tar.extractfile(info).read().decode("UTF-8")
                        repos.save_file(sPath,contents,group,mtime)


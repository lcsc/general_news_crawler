from pydantic import BaseModel, ConfigDict
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List, Dict

from datetime import datetime

class FileDb(BaseModel):
    id: Optional[PydanticObjectId] = None
    path:str
    group:str
    format:str
    contents:str
    modDate:datetime

class FilesRepository(AbstractRepository[FileDb]):
    class Meta:
        collection_name = 'Files'
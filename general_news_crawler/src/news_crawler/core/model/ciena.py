from pydantic import BaseModel, ConfigDict
from pydantic_mongo import PydanticObjectId,AbstractRepository
from typing import Optional, List, Dict

class CienaConfig(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    task: str
    model: str
    ciena_config:dict
    class Config:
        # Configuración para manejar la conversión con MongoDB
        arbitrary_types_allowed = True
        use_enum_values = True

class CienaConfigRepository(AbstractRepository[CienaConfig]):
    class Meta:
        collection_name = 'CienaConfig'
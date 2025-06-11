from dataclasses import dataclass
from sqlite3.dbapi2 import Timestamp
from pydantic import BaseModel, Field

@dataclass
class Contact:
    id:str
    name:str
    phone:str
    info:str
    info_boxes:str

class Message(BaseModel):
    content: str
    from_: str = Field(alias='from')
    type: str
    timestamp: int

class AskRequest(BaseModel):
    message: str
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Summaries(BaseModel):
    id: int
    created_at: datetime
    summary: Optional[str] = Field(None)
    vendor: Optional[str] = Field(None)
    link: Optional[str] = Field(None)
    title: Optional[str] = Field(None)
    
class Bookmarks(BaseModel):
    title: Optional[str] = Field(None)
    summary: Optional[str] = Field(None)
    link: Optional[str] = Field(None)
    vendor: Optional[str] = Field(None)
    summary_id:int 



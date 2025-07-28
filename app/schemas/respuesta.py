from pydantic import BaseModel

class TotalRegistrosResponse(BaseModel):
    total: int 
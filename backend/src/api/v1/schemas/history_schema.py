from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class GlobalStatsResponse(BaseModel):
    timestamp: datetime
    online: int
    offline: int
    reduced: int
    free: int
    total: int
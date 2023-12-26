import dataclasses
import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class FootballMatchDTOJSONEncoder(json.JSONEncoder):
    def default(self, o) -> Any:
        if isinstance(o, UUID):
            return str(o)

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, BaseModel):
            return o.dict()

        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        return json.JSONEncoder.default(self, o)

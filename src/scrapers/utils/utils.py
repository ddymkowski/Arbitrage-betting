import dataclasses
import json
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel


def generate_uuid():
    return str(uuid4())


class CustomEncoder(json.JSONEncoder):
    def default(self, o) -> Any:
        if isinstance(o, UUID):
            return o.hex

        if isinstance(o, Enum):
            return o.value

        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, BaseModel):
            return o.dict()

        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        return json.JSONEncoder.default(self, o)


def custom_json_serializer(d: dict[Any, Any]) -> dict[Any, Any]:
    return json.dumps(d, cls=CustomEncoder)

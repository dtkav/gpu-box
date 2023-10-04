from typing import Union, List, Any, Dict, IO
from dataclasses import dataclass

JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]

@dataclass
class File:
    path: str
    name: str
    contents: IO[bytes]
    content_type: str

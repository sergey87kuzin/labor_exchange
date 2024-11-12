from dataclasses import dataclass


@dataclass
class Response:
    id: int


@dataclass
class ResponseFull:
    id: int
    message: str

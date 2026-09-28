from dataclasses import dataclass


@dataclass
class CodeChunk:
    path: str
    language: str
    chunk_type: str
    symbol_name: str | None
    start_line: int
    end_line: int
    content: str

@dataclass
class CodeSearchResult:
    id: int
    path: str
    language: str
    chunk_type: str
    symbol_name: str | None
    start_line: int
    end_line: int
    content: str
    distance: float
    similarity: float
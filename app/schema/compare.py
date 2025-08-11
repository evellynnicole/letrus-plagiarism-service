# app/schema/compare.py
from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CompareMode(str, Enum):
    lexical = "lexical"  # TF-IDF
    semantic = "semantic"  # embeddings densos
    hybrid = "hybrid"  # embeddings densos + esparsos
    all = "all"  # léxico + dense + hybrid


class CompareRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Trecho a ser comparado")
    top_k: int = Field(5, ge=1, le=50, description="Qtde de documentos a retornar")
    mode: CompareMode = Field(
        CompareMode.all,
        description=(
            "Estratégia de busca:\n"
            "lexical: TF-IDF\n"
            "semantic: Apenas embeddings densos\n"
            "hybrid: Combina embeddings densos e esparsos (Léxico + Semantico)\n"
            "all: Retorna todas as estratégias\n"
            "default: all"
        ),
    )


class MatchItem(BaseModel):
    id: Optional[str] = None
    index: Optional[int] = None
    score: float
    text: str


class CompareResponse(BaseModel):
    mode: Literal["lexical", "semantic", "hybrid", "all"]
    lexical: List[MatchItem] = Field(default_factory=list)
    semantic: List[MatchItem] = Field(default_factory=list)
    hybrid: List[MatchItem] = Field(default_factory=list)

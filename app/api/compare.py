from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException

from app.config.config import Config
from app.schema.compare import (
    CompareMode,
    CompareRequest,
    CompareResponse,
    MatchItem,
)
from app.services.compare_service import CompareService

router = APIRouter()


@lru_cache
def get_service() -> CompareService:
    cfg = Config()
    return CompareService(cfg)


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post(
    "/compare",
    response_model=CompareResponse,
    response_model_exclude_none=True,
    summary="Compara um texto com um corpus utilizando diferentes estratégias de busca",
    description=(
        "Estratégias do campo 'mode':\n\n"
        "lexical: TF-IDF\n\n"
        "semantic: Apenas embeddings densos\n\n"
        "hybrid: Combina embeddings densos e esparsos (Léxico + Semantico)\n\n"
        "all: Retorna todas as estratégias\n\n"
        "default: all"
    ),
)
def compare(body: CompareRequest, svc: CompareService = Depends(get_service)):
    if not body.text.strip():
        raise HTTPException(status_code=422, detail="Campo 'text' não pode ser vazio.")

    try:
        if body.mode == CompareMode.lexical:
            lex = svc.compare_lexical(body.text, top_k=body.top_k)
            return CompareResponse(mode="lexical", lexical=[MatchItem(**r) for r in lex])

        if body.mode == CompareMode.semantic:
            den = svc.compare_semantic(body.text, top_k=body.top_k)
            return CompareResponse(mode="semantic", semantic=[MatchItem(**r) for r in den])

        if body.mode == CompareMode.hybrid:
            hyb = svc.compare_hybrid(body.text, top_k=body.top_k)
            return CompareResponse(mode="hybrid", hybrid=[MatchItem(**r) for r in hyb])

        lex = svc.compare_lexical(body.text, top_k=body.top_k)
        den = svc.compare_semantic(body.text, top_k=body.top_k)
        hyb = svc.compare_hybrid(body.text, top_k=body.top_k)
        return CompareResponse(
            mode="all",
            lexical=[MatchItem(**r) for r in lex],
            semantic=[MatchItem(**r) for r in den],
            hybrid=[MatchItem(**r) for r in hyb],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao comparar textos.") from e

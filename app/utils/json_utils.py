# app/utils/json_utils.py
import json
import os
from typing import Any, Dict, Iterable, List


def load_pt_corpus_from_jsonl(path: str) -> List[str]:
    """Carrega uma lista de textos a partir de um arquivo .jsonl com chave 'text'."""
    texts: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                txt = obj.get("text")
                if isinstance(txt, str) and txt.strip():
                    texts.append(txt)
    return texts


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    if not os.path.exists(path):
        print(f"Arquivo não encontrado: {path}", flush=True)
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                o = json.loads(line)
            except Exception:
                continue
            text = (o.get("text") or "").strip()
            if not text:
                continue
            yield {"id": o.get("id"), "text": text}

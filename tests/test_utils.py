import os
import tempfile

from app.utils.json_utils import iter_jsonl, load_pt_corpus_from_jsonl

LEN_CORPUS = 2


def test_load_corpus_basic():
    """Testa carregamento básico do corpus"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write('{"id": "doc1", "text": "Texto 1"}\n')
        f.write('{"id": "doc2", "text": "Texto 2"}\n')
        temp_file = f.name

    try:
        texts = load_pt_corpus_from_jsonl(temp_file)
        assert len(texts) == LEN_CORPUS
        assert texts[0] == "Texto 1"
        assert texts[1] == "Texto 2"
    finally:
        os.unlink(temp_file)


def test_iter_jsonl_basic():
    """Testa iteração básica sobre JSONL"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write('{"id": "doc1", "text": "Texto 1"}\n')
        f.write('{"id": "doc2", "text": "Texto 2"}\n')
        temp_file = f.name

    try:
        items = list(iter_jsonl(temp_file))
        assert len(items) == LEN_CORPUS
        assert items[0]["id"] == "doc1"
        assert items[1]["text"] == "Texto 2"
    finally:
        os.unlink(temp_file)


def test_empty_file():
    """Testa arquivo vazio"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        temp_file = f.name

    try:
        texts = load_pt_corpus_from_jsonl(temp_file)
        assert texts == []
    finally:
        os.unlink(temp_file)


def test_invalid_lines():
    """Testa linhas inválidas"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write('{"id": "doc1", "text": "Texto válido"}\n')
        f.write("linha inválida\n")
        f.write('{"id": "doc2", "text": "Outro texto válido"}\n')
        temp_file = f.name

    try:
        texts = load_pt_corpus_from_jsonl(temp_file)
        assert len(texts) == LEN_CORPUS
        assert "Texto válido" in texts
        assert "Outro texto válido" in texts
    finally:
        os.unlink(temp_file)

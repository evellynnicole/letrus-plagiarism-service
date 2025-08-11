import os
import tempfile

from app.utils.json_utils import iter_jsonl, load_pt_corpus_from_jsonl


def test_load_pt_corpus_from_jsonl():
    """Testa carregamento básico do corpus"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write('{"id": "doc1", "text": "Texto 1"}\n')
        f.write('{"id": "doc2", "text": "Texto 2"}\n')
        temp_file = f.name

    try:
        texts = load_pt_corpus_from_jsonl(temp_file)
        assert len(texts) == 2
        assert texts[0] == "Texto 1"
        assert texts[1] == "Texto 2"
    finally:
        os.unlink(temp_file)


def test_iter_jsonl():
    """Testa iteração básica sobre JSONL"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsonl", delete=False, encoding="utf-8"
    ) as f:
        f.write('{"id": "doc1", "text": "Texto 1"}\n')
        f.write('{"id": "doc2", "text": "Texto 2"}\n')
        temp_file = f.name

    try:
        items = list(iter_jsonl(temp_file))
        assert len(items) == 2
        assert items[0]["id"] == "doc1"
        assert items[1]["text"] == "Texto 2"
    finally:
        os.unlink(temp_file)

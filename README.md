# Letrus Plagiarism Service

Serviço de comparação/similaridade textual para detecção de plágio, com três estratégias:

- **Léxico (TF‑IDF)**: Análise baseada em frequência de termos, rápida e eficiente para detecção de cópia direta
- **Semântico (embeddings densos)**: Compreensão semântica via Sentence Transformers, captura similaridade conceitual
- **Híbrido (fusão RRF)**: Combina o melhor dos dois mundos - precisão semântica + robustez lexical

A API é construída com FastAPI e exposta em `/docs`.

## Sumário
- [Arquitetura](#arquitetura)
- [Requisitos](#requisitos)
- [Execução com Docker Compose (recomendado)](#execução-com-docker-compose-recomendado)
- [Execução local (sem Docker)](#execução-local-sem-docker)
- [Uso da API](#uso-da-api)
- [Testes](#testes)
- [Configuração](#configuração)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Solução de problemas](#solução-de-problemas)


## Arquitetura
- `FastAPI` expõe os endpoints (`/health`, `/compare`).
- Camada de serviço (`CompareService`) orquestra:
  - **Léxico**: TF‑IDF local com `scikit-learn` - rápido e eficiente para detecção de cópia direta
  - **Semântico**: Qdrant como vetor DB com embeddings densos via Sentence Transformers
  - **Híbrido**: Fusão RRF (Reciprocal Rank Fusion) entre denso e esparso (BM25) - combina precisão semântica com robustez lexical
- `scripts/indexer.py` cria/garante coleções no Qdrant e indexa o corpus.
- `scripts/download_data.py` baixa um subconjunto do Wikipedia PT e salva em `data/raw`.

### Por que a estratégia híbrida?

A estratégia híbrida combina as vantagens de ambas as abordagens:
- **Léxico (TF-IDF)**: Excelente para detectar cópias diretas, paráfrases e reordenações de frases
- **Semântico (embeddings)**: Captura similaridade conceitual mesmo quando as palavras são diferentes
- **Fusão RRF**: Combina os rankings de ambas as estratégias de forma inteligente, priorizando documentos que aparecem bem posicionados em ambas as listas

Esta abordagem é especialmente eficaz para detecção de plágio em português, onde variações linguísticas e sinônimos são comuns.


## Requisitos
- Python 3.12+
- Docker e Docker Compose (para semântico/híbrido e execução completa)


## Execução com Docker Compose (recomendado)
Este é o caminho mais simples para subir tudo (Qdrant + indexação + API).

**⚠️ Importante**: Na primeira execução, o serviço pode demorar alguns minutos para subir devido ao download dos modelos de linguagem (Sentence Transformers). Este é um processo único - nas próximas execuções será muito mais rápido.

**📁 Pré-requisito**: Certifique-se de que o arquivo `data/raw/wikipedia-PT-300.jsonl` existe no projeto. Este arquivo contém o corpus que será indexado no Qdrant.

1) Subir os serviços:
   ```bash
   docker compose up --build
   ```

   O fluxo será:
   - `qdrant` sobe e fica disponível em `localhost:6333`.
   - `indexer` espera o `qdrant` estar saudável e indexa o corpus nas coleções configuradas.
   - `api` inicia após o `indexer` concluir com sucesso, expondo a API em `http://localhost:8000`.

   **⏱️ Tempo de inicialização**: Na primeira execução, pode levar demorar devido ao download dos modelos de linguagem. Nas próximas execuções será muito mais rápido.

2) Acesse a documentação interativa em:
   - `http://localhost:8000/docs`
   - `http://localhost:8000/redoc`


## Execução local (sem Docker)
Você pode rodar a API localmente para testar o modo léxico (TF‑IDF) sem Qdrant. Para semântico/híbrido, prefira o Docker Compose.

**⚠️ Nota**: Para usar estratégias semânticas/híbridas localmente, você precisará ajustar a configuração do Qdrant para `localhost:6333` em vez de `http://qdrant:6333`.

**📁 Pré-requisito**: Certifique-se de que o arquivo `data/raw/wikipedia-PT-300.jsonl` existe no projeto.

1) Ambiente e dependências:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Rodar a API (atenção: sem Qdrant, use `mode=lexical` nos requests):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


## Uso da API
### Healthcheck
```bash
curl -s http://localhost:8000/health
```

### Comparação (POST /compare)
Body:
```json
{
  "text": "Seu trecho aqui",
  "top_k": 5,
  "mode": "all" // "lexical" | "semantic" | "hybrid" | "all"
}
```

Exemplos:
- Léxico (não requer Qdrant):
  ```bash
  curl -s -X POST http://localhost:8000/compare \
    -H 'Content-Type: application/json' \
    -d '{"text": "A linguagem Python é...", "top_k": 5, "mode": "lexical"}' | jq
  ```

- Semântico (requer Qdrant ativo e corpus indexado):
  ```bash
  curl -s -X POST http://localhost:8000/compare \
    -H 'Content-Type: application/json' \
    -d '{"text": "A linguagem Python é...", "top_k": 5, "mode": "semantic"}' | jq
  ```

- Híbrido (requer Qdrant):
  ```bash
  curl -s -X POST http://localhost:8000/compare \
    -H 'Content-Type: application/json' \
    -d '{"text": "A linguagem Python é...", "top_k": 5, "mode": "hybrid"}' | jq
  ```

- Todas as estratégias (requer Qdrant):
  ```bash
  curl -s -X POST http://localhost:8000/compare \
    -H 'Content-Type: application/json' \
    -d '{"text": "A linguagem Python é...", "top_k": 5, "mode": "all"}' | jq
  ```

Respostas seguem o schema:
```json
{
  "mode": "all",
  "lexical": [{"index": 123, "score": 0.78, "text": "..."}],
  "semantic": [{"id": "...", "score": 0.82, "text": "..."}],
  "hybrid": [{"id": "...", "score": 0.86, "text": "..."}]
}
```


## Testes
Rodar localmente:
```bash
pytest -q
```

Observações:
- Para que os testes que exercitam o endpoint `/compare` passem em modo padrão (`mode=all`), é necessário que:
  1) O dataset exista em `data/raw/wikipedia-PT-300.jsonl` (rode `python -m scripts.download_data`).
  2) O Qdrant esteja rodando e as coleções estejam indexadas (use `docker compose up` antes de executar os testes).


## Configuração
As configurações padrão estão em `app/config/config.py`:

- `qdrant_url`: URL do Qdrant 
  - **Docker Compose**: `http://qdrant:6333` (padrão)
  - **Execução local**: `http://localhost:6333` (ajuste necessário)
- `model_dense_name`: Modelo de embeddings densos (Sentence Transformers).
- `model_sparse_name`: Modelo esparso (BM25 via Qdrant).
- `dense_name` / `sparse_name`: nomes dos espaços vetoriais nas coleções.
- `qdrant_collection_hybrid` / `qdrant_collection_dense`: nomes das coleções.
- `data_path`: caminho do JSONL com o corpus (padrão: `data/raw/wikipedia-PT-300.jsonl`).

**⚠️ Para execução local**: Se você quiser usar estratégias semânticas/híbridas sem Docker, altere `qdrant_url` para `http://localhost:6333` no arquivo de configuração.

Sugestão futura: externalizar essas configurações via variáveis de ambiente.


## Estrutura do projeto
```
app/
  ai/
    lexical/tfidf.py           # Similaridade TF‑IDF
    semantic/indexer.py        # Criação/garantia de coleções e upsert no Qdrant
    semantic/retriever.py      # Buscas dense-only e híbridas (RRF)
  api/compare.py               # Rotas FastAPI
  services/compare_service.py  # Orquestra léxico/semântico
  schema/compare.py            # Pydantic models
  utils/json_utils.py          # Leitura de JSONL
  main.py                      # Criação do app FastAPI

scripts/
  download_data.py             # Baixa Wikipedia PT (amostras)
  indexer.py                   # Indexa no Qdrant

docker-compose.yml             # Orquestra qdrant + indexer + api
Dockerfile                     # Imagem da API
tests/                         # Testes básicos de rota
```


## Solução de problemas
- Erro: `Nenhum texto encontrado em data/raw/wikipedia-PT-300.jsonl`
  - Certifique-se de que o arquivo `data/raw/wikipedia-PT-300.jsonl` existe no projeto.

- Erro de conexão com Qdrant ao usar `semantic`/`hybrid`/`all`:
  - Garanta que o Qdrant está rodando (no Compose, ele sobe automaticamente) e que as coleções foram criadas/indexadas pelo `indexer`.
  - **Para execução local**: Verifique se a URL do Qdrant está configurada como `http://localhost:6333`.

- **Modelos levam muito tempo para baixar na primeira execução**:
  - É esperado para o `SentenceTransformer` (pode levar 3-5 minutos na primeira vez).
  - O cache é reutilizado nas próximas execuções do container/host.
  - Este é um processo único - nas próximas execuções será muito mais rápido.

- Execução local sem Docker não encontra Qdrant:
  - Prefira usar `mode=lexical` ou suba tudo via Docker Compose.
  - **Alternativa**: Se você tiver Qdrant rodando localmente, ajuste a configuração para `http://localhost:6333`.

- **Serviço demora para subir**:
  - Na primeira execução, é normal demorar alguns minutos devido ao download dos modelos.
  - Verifique os logs do container para acompanhar o progresso.
  - Nas próximas execuções será muito mais rápido.


---
Feito para o desafio técnico. Qualquer dúvida, verifique `/docs` e os arquivos em `app/` e `scripts/`.
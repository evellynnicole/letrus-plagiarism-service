# Letrus Plagiarism Service

Um serviço de detecção de plágio que combina abordagens léxicas e semânticas para identificar similaridades entre textos em português.

## Sobre o Projeto


- **Análise Léxica (TF-IDF)**: Identifica similaridades baseadas em palavras e frases exatas
- **Análise Semântica (Embeddings)**: Captura similaridades de significado e contexto
- **Busca Híbrida**: Combina ambas as abordagens para máxima precisão
- **Modo Completo**: Permite executar todas as estratégias simultaneamente

### Como Funciona a Busca Híbrida

A busca híbrida usa **RRF (Reciprocal Rank Fusion)** para combinar resultados de duas abordagens:

1. **Fusão RRF**: Combina rankings de embeddings densos (semântica) + BM25 (léxica) para ordenar candidatos
2. **Similaridade Final**: Refina os melhores candidatos obtendo a similaridade de cosseno.

### Componentes Principais

- **FastAPI**: API REST para exposição dos serviços
- **Qdrant**: Banco de dados vetorial para armazenamento e busca de embeddings
- **FastEmbed**: Geração de embeddings densos (substituindo sentence-transformers)
- **Scikit-learn**: Implementação do TF-IDF para análise léxica

## Como Executar

### Pré-requisitos

- Docker e Docker Compose
- Python 3.8+

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd letrus-plagiarism-service
```

### 2. Executar com Docker Compose

**Recomendado**: Use Docker Compose para execução mais simples:

```bash
docker-compose up --build
```

**Se você usar Docker Compose, não precisa alterar nenhuma configuração!**

O sistema irá:
1. Iniciar o Qdrant na porta 6333
2. Executar o indexador para criar os índices
3. Iniciar a API na porta 8000

### 3. Acessar a API

- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Endpoint Principal**: POST http://localhost:8000/compare
- **Dashboard Qdrant**: http://localhost:6333/dashboard

## Configurações e Escolhas Técnicas

### Por que não usar variáveis de ambiente?

Optei por não usar variáveis de ambiente para **facilitar o desenvolvimento e demonstração**. Em um ambiente de produção, seria recomendado usar.


### Configuração para Execução Local

Se você quiser executar **fora do Docker**, precisará alterar a URL do Qdrant no arquivo `app/config/config.py`:

```python
# Linha 3 do arquivo app/config/config.py
self.qdrant_url = "http://localhost:6333"  # Altere de "http://qdrant:6333" para "http://localhost:6333"
```

### Por que FastEmbed ao invés de sentence-transformers?

A escolha pelo **FastEmbed** foi baseada em:

1. **Performance**: Mais rápido para inferência
2. **Memória**: Menor uso de RAM
3. **Simplicidade**: API mais simples e direta
4. **Compatibilidade**: Funciona bem com o Qdrant


## Uso da API

### Exemplo de Requisição

```bash
curl -X POST "http://localhost:8000/compare" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Texto para comparar",
       "mode": "all",
       "top_k": 1
     }'
```

### Modos de Comparação

- **`lexical`**: Análise TF-IDF para plágio direto e cópias literais
- **`semantic`**: Embeddings densos (all-MiniLM-L6-v2) para plágio parafraseado e similaridades semânticas
- **`hybrid`**: Combinação otimizada de embeddings densos (all-MiniLM-L6-v2) com BM25 (vetor esparso)
- **`all`**: Executa todas as estratégias para cobertura completa

### Estrutura da Resposta

A API retorna um objeto `CompareResponse` com os seguintes campos:

```json
{
  "mode": "all",
  "lexical": [
    {
      "index": 42,
      "similarity": 0.85,
      "text": "Texto similar encontrado via TF-IDF"
    }
  ],
  "semantic": [
    {
      "id": "doc_123",
      "similarity": 0.92,
      "text": "Texto similar encontrado via embeddings"
    }
  ],
  "hybrid": [
    {
      "id": "doc_456",
      "similarity": 0.95,
      "text": "Texto similar encontrado via busca híbrida"
    }
  ]
}
```

**Campos de cada item:**
- **`id`**: Identificador único do documento (quando disponível)
- **`index`**: Posição no corpus (para busca léxica)
- **`similarity`**: Pontuação de similaridade de cosseno (0.0 a 1.0, onde 1.0 = idêntico)
- **`text`**: Conteúdo do documento similar encontrado

## Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=app
```

## 📁 Estrutura do Projeto

```
app/
├── api/                    # Endpoints da API
│   └── compare.py         # Endpoint principal de comparação
├── services/              # Lógica de negócio
│   └── compare_service.py # Orquestrador dos serviços
├── ai/                    # Implementações de IA
│   ├── lexical/          # TF-IDF
│   └── semantic/         # Embeddings e busca vetorial
├── config/               # Configurações
└── utils/                # Utilitários

scripts/
├── indexer.py            # Script de indexação
└── download_data.py      # Download do corpus

data/                     # Corpus de textos
```

## Funcionalidades Implementadas

✅ **API REST com FastAPI**  
✅ **Análise Léxica com TF-IDF**  
✅ **Análise Semântica com Embeddings (all-MiniLM-L6-v2)**  
✅ **Busca Híbrida (all-MiniLM-L6-v2 + BM25)**  
✅ **Indexação Automática com Qdrant**  
✅ **Dockerização Completa**  
✅ **Health Check**  
✅ **Documentação Automática (Swagger/ReDoc)**  
✅ **Tratamento de Erros**  
✅ **Validação de Entrada**  


## Otimizações Implementadas

### Sistema de Hash 

O indexador implementa uma **abordagem de hash SHA-1** para otimizar a reindexação.

**Benefícios:**
- **Reindexação Inteligente**: Só reindexa documentos que realmente mudaram
- **Performance**: Evita reprocessar textos idênticos
- **Eficiência**: Compara hashes antes de fazer upsert no Qdrant
- **Idempotência**: Pode ser executado múltiplas vezes sem duplicar dados


## Referências

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [FastEmbed Documentation](https://github.com/qdrant/fastembed)
- [Scikit-learn TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)

## Contribuição

Este projeto foi desenvolvido como parte de um case técnico para a Letrus.

**Desenvolvedora:** [evellynnicole](https://github.com/evellynnicole)

---


# Letrus Plagiarism 

Um serviço de detecção de plágio que combina abordagens léxicas e semânticas para identificar similaridades entre textos em português.

## Sobre o Projeto

Este projeto implementa um sistema **completo de detecção de plágio** que oferece **todas as estratégias** de análise:

- **Análise Léxica (TF-IDF)**: Identifica similaridades baseadas em palavras e frases exatas
- **Análise Semântica (Embeddings)**: Captura similaridades de significado e contexto
- **Busca Híbrida**: Combina ambas as abordagens para máxima precisão
- **Modo Completo**: Permite executar todas as estratégias simultaneamente

##  Arquitetura da Solução

### Por que Múltiplas Abordagens?

A solução implementa **todas as estratégias** de detecção de plágio para cobrir todos os cenários possíveis:

1. **Análise Léxica (TF-IDF)**: Detecta plágio direto, cópias literais e similaridades baseadas em palavras
2. **Análise Semântica (Embeddings)**: Captura plágio parafraseado, reescrito e similaridades de significado
3. **Busca Híbrida**: Combina ambas as abordagens para máxima precisão e cobertura
4. **Modo "All"**: Permite comparar todas as estratégias simultaneamente

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

```python
# Antes (sentence-transformers):
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode([text])

# Agora (FastEmbed):
from fastembed import TextEmbedding
model = TextEmbedding('sentence-transformers/all-MiniLM-L6-v2')
embeddings = list(model.embed([text]))
```

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
- **`semantic`**: Embeddings densos para plágio parafraseado e similaridades semânticas
- **`hybrid`**: Combinação otimizada de ambas as abordagens
- **`all`**: Executa todas as estratégias para cobertura completa

### Estrutura da Resposta

A API retorna um objeto `CompareResponse` com os seguintes campos:

```json
{
  "mode": "all",
  "lexical": [
    {
      "index": 42,
      "score": 0.85,
      "text": "Texto similar encontrado via TF-IDF"
    }
  ],
  "semantic": [
    {
      "id": "doc_123",
      "score": 0.92,
      "text": "Texto similar encontrado via embeddings"
    }
  ],
  "hybrid": [
    {
      "id": "doc_456",
      "score": 0.95,
      "text": "Texto similar encontrado via busca híbrida"
    }
  ]
}
```

**Campos de cada item:**
- **`id`**: Identificador único do documento (quando disponível)
- **`index`**: Posição no corpus (para busca léxica)
- **`score`**: Pontuação de similaridade (0.0 a 1.0, onde 1.0 = idêntico)
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
qdrant_data/             # Dados do Qdrant
```

## 🔍 Funcionalidades Implementadas

✅ **API REST com FastAPI**  
✅ **Análise Léxica com TF-IDF**  
✅ **Análise Semântica com Embeddings**  
✅ **Busca Híbrida (Dense + Sparse)**  
✅ **Indexação Automática com Qdrant**  
✅ **Dockerização Completa**  
✅ **Health Check**  
✅ **Documentação Automática (Swagger/ReDoc)**  
✅ **Tratamento de Erros**  
✅ **Validação de Entrada**  

## Cobertura Completa de Cenários

O sistema foi projetado para detectar **todos os tipos de plágio**:

- **Plágio Direto**: Cópias literais de texto
- **Plágio Parafraseado**: Texto reescrito com palavras diferentes
- **Plágio Misto**: Combinações de cópia e reescrita
- **Similaridade Parcial**: Trechos similares em textos diferentes
- **Plágio de Estrutura**: Organização similar de ideias

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


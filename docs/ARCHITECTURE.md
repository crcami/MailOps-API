# Arquitetura MailOps AI API

## Stack Tecnológica

- **Framework**: FastAPI
- **Banco de Dados**: SQLite (configurável para PostgreSQL/MySQL)
- **ORM**: SQLAlchemy
- **Autenticação**: JWT (PyJWT)
- **IA/ML**: Suporte para múltiplos providers (local ML, OpenAI, Anthropic)
- **NLP**: spaCy, scikit-learn
- **Email**: SMTP para envio de emails

## Estrutura do Projeto

```
MailOps-API/
├── app/
│   ├── api/              # Camada de API
│   │   ├── routers/      # Endpoints (auth, analyze)
│   │   ├── schemas/      # Modelos Pydantic
│   │   └── deps.py       # Dependências (auth, validação)
│   ├── core/             # Configurações e segurança
│   │   ├── config.py     # Settings da aplicação
│   │   ├── security.py   # JWT, hashing de senha
│   │   └── logging.py    # Configuração de logs
│   ├── db/               # Camada de dados
│   │   ├── models.py     # Modelos SQLAlchemy
│   │   ├── session.py    # Sessão do banco
│   │   └── base.py       # Inicialização do DB
│   ├── services/         # Lógica de negócio
│   │   ├── ai/           # Integração com providers de IA
│   │   ├── classifier.py # Classificação de emails
│   │   ├── intent.py     # Detecção de intenção
│   │   ├── replies.py    # Geração de respostas
│   │   ├── email_extractor.py
│   │   └── nlp.py        # Processamento de linguagem natural
│   └── main.py           # Entrypoint da aplicação
├── data/                 # Dados de treinamento/classificação
├── scripts/              # Scripts utilitários
└── docs/                 # Documentação
```

## Padrões de Design

### Arquitetura em Camadas

1. **API Layer** (`app/api/`): Endpoints REST, validação de entrada via Pydantic
2. **Service Layer** (`app/services/`): Lógica de negócio reutilizável
3. **Data Layer** (`app/db/`): Acesso ao banco via ORM

### Dependency Injection

FastAPI usa injeção de dependências para:

- Autenticação (API Key + JWT)
- Sessões de banco de dados
- Validação de permissões

### Factory Pattern

`services/ai/factory.py` - Criação dinâmica de clientes IA baseado em configuração:

```python
AI_PROVIDER=local_ml   # ou openai, anthropic
```

## Fluxo de Análise de Email

1. **Recebimento**: POST `/api/analyze` com email (texto ou PDF)
2. **Extração**: Parser extrai conteúdo e metadados
3. **Classificação**: ML classifica em categorias (RH, SAC, etc.)
4. **Detecção de Intenção**: Identifica propósito (reclamação, dúvida, etc.)
5. **Extração de Dados**: Regex/NLP extrai emails, telefones
6. **Resposta**: IA gera sugestão de resposta contextualizada

## Segurança

- **Hashing de Senhas**: bcrypt
- **JWT Tokens**: HS256, expiração configurável
- **Política de Senha**: Validação de complexidade
- **API Key**: Proteção de acesso público
- **CORS**: Configurável via `API_CORS_ORIGINS`

## Modelos de Dados

### User

- `id`, `email`, `hashed_password`
- `is_active`, `created_at`, `updated_at`

### PasswordResetToken

- `id`, `user_id`, `token`, `expires_at`
- `used_at`, `created_at`

## Providers de IA

### Local ML (Padrão)

- Classificação com scikit-learn
- NLP com spaCy
- Sem dependências externas

### OpenAI

- GPT models para análise e geração
- Requer `OPENAI_API_KEY`

### Anthropic

- Claude models
- Requer `ANTHROPIC_API_KEY`

## Extensibilidade

### Adicionar Nova Categoria

1. Atualizar `data/categories.json`
2. Treinar modelo com novos exemplos
3. Atualizar `services/classifier.py`

### Adicionar Novo Provider de IA

1. Criar classe em `services/ai/`
2. Implementar interface padrão
3. Registrar em `factory.py`

## Health Check

GET `/api/health` - Verifica status da aplicação

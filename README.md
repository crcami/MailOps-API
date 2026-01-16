# MailOps AI API

API inteligente para análise e classificação automática de emails usando IA/ML.

## Início Rápido

### Pré-requisitos

- Python 3.8+
- pip

### Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd MailOps-API

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações
```

### Executando

```bash
uvicorn app.main:app --reload --port 8000
```

Acesse a documentação interativa em: `http://localhost:8000/docs`

## Autenticação

A API utiliza **dupla camada de autenticação**:

1. **API Key** (`X-API-Key` header) - obrigatória em todas as rotas
2. **JWT Token** (`Authorization: Bearer <token>`) - para rotas protegidas

**Fluxo de uso:**

1. Configure `X-API-Key` no Swagger (botão Authorize)
2. Faça login via `/api/auth/login`
3. Use o token JWT retornado nas rotas protegidas

## Funcionalidades

- **Análise de Emails**: Classificação automática por categoria e intenção
- **Extração de Dados**: Identifica emails, telefones e informações relevantes
- **Respostas Inteligentes**: Gera sugestões de resposta baseadas no contexto
- **Autenticação Completa**: Sistema de login, registro e recuperação de senha

## Arquitetura

Para detalhes sobre a estrutura do projeto, tecnologias utilizadas e padrões de design, consulte [ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Variáveis de Ambiente

Principais variáveis (veja `.env.example` para lista completa):

- `DATABASE_URL`: Conexão com banco de dados (SQLite por padrão)
- `SECRET_KEY`: Chave secreta para JWT
- `PUBLIC_API_KEY`: API key para acesso público
- `AI_PROVIDER`: Provider de IA (`local_ml`, `openai`, `anthropic`)
- `SMTP_*`: Configurações de email (opcional)

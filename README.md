# 🚀 Otimizador de Entrevistas com Inteligência Artificial

Sistema completo de otimização de entrevistas que utiliza Machine Learning para identificar os candidatos mais compatíveis com vagas específicas, desenvolvido com Flask, PostgreSQL, Docker e monitorização avançada.

## 📋 Índice

- [Características](#características)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e Execução](#instalação-e-execução)
- [Uso da Aplicação](#uso-da-aplicação)
- [API REST](#api-rest)
- [Monitorização](#monitorização)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

## ✨ Características

- **🧠 Machine Learning Aprimorado**: Modelo Random Forest com 7 features avançadas incluindo TF-IDF, compatibilidade técnica, acadêmica e linguística
- **🗄️ Banco PostgreSQL**: Banco de dados robusto com índices GIN para busca full-text em português
- **🌐 Interface Web**: Dashboard intuitivo para visualização de vagas e candidatos
- **📊 Score de Compatibilidade**: Probabilidade de contratação baseada em dados históricos
- **🔍 Busca Avançada**: Sistema de busca full-text otimizado com PostgreSQL
- **📈 Monitorização**: Prometheus e Grafana para métricas em tempo real
- **🐳 Containerização**: Deploy completo com Docker e Docker Compose
- **🛡️ Segurança**: Implementação de boas práticas de segurança
- **🧪 Testes**: Suite completa de testes unitários e de integração

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│   Flask App     │────│   Prometheus    │
│ (Load Balancer) │    │ (API + Web UI)  │    │   (Metrics)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │     Grafana     │
                       │   Database      │    │  (Dashboard)    │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │ Machine Learning│
                       │    Pipeline     │
                       └─────────────────┘
```

## 📦 Pré-requisitos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**

## 🚀 Instalação e Execução

### 1. Clone o Repositório

```bash
git clone <repository-url>
cd otimizador-entrevistas
```

### 2. Executar com Docker

#### Stack Completa (Recomendado)
```bash
# Executar toda a stack (PostgreSQL + App + Prometheus + Grafana)
docker-compose up --build

# Executar em background
docker-compose up -d --build
```

#### Verificar Status dos Serviços
```bash
# Verificar containers rodando
docker-compose ps

# Verificar logs da aplicação
docker-compose logs app

# Verificar logs do PostgreSQL
docker-compose logs postgresql
```

#### Comandos Úteis
```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (dados)
docker-compose down -v

# Reconstruir apenas a aplicação
docker-compose up --build app

# Executar comandos dentro do container
docker-compose exec app bash
docker-compose exec postgresql psql -U postgres -d otimizador_entrevistas
```

**⚠️ IMPORTANTE**: Na primeira execução, o sistema:
1. **Verificará automaticamente** se o PostgreSQL está disponível
2. **Criará o esquema do banco** se não existir
3. **Populará automaticamente** com os dados dos arquivos JSON
4. **Migrará** vagas, candidatos e prospects para PostgreSQL

Este processo pode levar alguns minutos na primeira execução. As execuções subsequentes serão mais rápidas pois os dados já estarão no banco.

## 🌐 Acesso aos Serviços

Após a execução com `docker-compose up`:

- **🖥️ Aplicação Principal**: http://localhost
- **🗄️ PostgreSQL**: localhost:5432 (acesso interno)
- **📊 Prometheus**: http://localhost:9090
- **📈 Grafana**: http://localhost:3000
  - Usuário: `admin`
  - Senha: `admin123`

## 🗄️ Inicialização Automática do Banco de Dados

### Processo Automático
A aplicação possui **inicialização automática do PostgreSQL** que é executada durante o startup:

1. **🔍 Verificação**: Detecta se PostgreSQL está disponível
2. **🏗️ Criação do Esquema**: Cria tabelas se não existirem
3. **📊 Verificação de Dados**: Checa se já existem dados no banco
4. **🚀 Migração Automática**: Migra dados JSON → PostgreSQL se necessário
5. **✅ Validação**: Confirma que a migração foi bem-sucedida

### Tabelas Criadas Automaticamente
- **`vagas`**: Informações das vagas com índices otimizados
- **`candidatos`**: Perfis dos candidatos
- **`prospects`**: Histórico de candidaturas (variável alvo para ML)
- **`predicoes`**: Resultados das predições do modelo

### Logs de Inicialização
Durante o startup, você verá logs como:
```
🔍 Verificando estado do banco de dados PostgreSQL...
✅ PostgreSQL está disponível!
📝 Banco vazio detectado. Iniciando população automática...
🚀 Configurando banco de dados PostgreSQL...
📋 Criando tabelas PostgreSQL...
🚀 Migrando dados para PostgreSQL...
✅ PostgreSQL configurado e populado com sucesso!
🎉 Banco de dados inicializado com sucesso!
```

### Fallback Inteligente
Se PostgreSQL não estiver disponível, a aplicação automaticamente:
- ⚠️ Detecta a indisponibilidade do banco
- 🔄 Ativa modo fallback JSON
- 📁 Carrega dados diretamente dos arquivos JSON
- 🚀 Continua funcionando normalmente

## 💻 Uso da Aplicação

### Dashboard Principal
1. Acesse http://localhost
2. Visualize todas as vagas disponíveis
3. Use filtros de busca por título, cliente ou nível

### Análise de Compatibilidade
1. Clique em "Ver Candidatos Compatíveis" em qualquer vaga
2. Visualize candidatos ordenados por score de compatibilidade (baseado em dados do PostgreSQL)
3. Analise informações detalhadas de cada candidato
4. Use busca full-text avançada para encontrar competências específicas

### Interpretação dos Scores
- **🟢 80-100%**: Excelente compatibilidade
- **🔵 60-79%**: Boa compatibilidade  
- **🟡 40-59%**: Compatibilidade regular
- **🔴 0-39%**: Baixa compatibilidade

## 🔌 API REST

### Endpoint de Predição

```bash
POST /api/predict
Content-Type: application/json

{
  "competencias_combinadas": "python flask django postgresql",
  "nivel_profissional": "senior",
  "areas_atuacao": "desenvolvimento"
}
```

**Resposta:**
```json
{
  "prediction": 1,
  "probability": {
    "not_hired": 0.3,
    "hired": 0.7
  },
  "match_score": 70.0
}
```

### Health Check

```bash
GET /health
```

## 📊 Monitorização

### Prometheus
- **URL**: http://localhost:9090
- **Métricas Coletadas**:
  - Requisições HTTP por endpoint
  - Tempo de resposta
  - Uso de CPU e memória
  - Erros da aplicação

### Grafana
- **URL**: http://localhost:3000
- **Login**: admin/admin123
- **Dashboards Incluídos**:
  - **Dashboard Principal**: Métricas da aplicação, ML e performance
  - **Dashboard de Infraestrutura**: Status dos containers e recursos do sistema

### Dashboards Automáticos

Os dashboards são automaticamente configurados ao iniciar o Grafana:

1. **Dashboard Principal** (`main-dashboard.json`):
   - Taxa de requisições por segundo
   - Tempo de resposta (95th percentile) 
   - Total de requisições por endpoint
   - Taxa de sucesso das requisições
   - Predições de ML por hora
   - Tempo de resposta das predições

2. **Dashboard de Infraestrutura** (`infrastructure-dashboard.json`):
   - Status dos containers (Flask, PostgreSQL, Prometheus, Nginx)
   - Conexões PostgreSQL ativas
   - Transações de banco de dados
   - Uso de memória e CPU por container

### Acesso Rápido
- **Aplicação**: http://localhost
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

## 🧪 Testes

### Executar Testes no Docker

```bash
# Executar testes dentro do container
docker-compose exec app python -m pytest tests/ -v

# Executar testes com cobertura
docker-compose exec app python -m pytest tests/ --cov=app --cov-report=html
```

## 🔬 Treinamento do Modelo

### Executar Treinamento via Docker

```bash
# Acessar o container da aplicação
docker-compose exec app bash

# Executar o notebook de treinamento
cd notebooks
jupyter nbconvert --to notebook --execute Treinamento.ipynb --output Treinamento_executed.ipynb
```

### Workflow dos Notebooks

O projeto utiliza dois notebooks para o treinamento:

1. **`Treinamento.ipynb`** - Notebook principal para desenvolvimento
   - Contém o pipeline completo de Machine Learning
   - Configuração e migração automática para PostgreSQL
   - Versionado no Git

2. **`Treinamento_executed.ipynb`** - Notebook executado automaticamente
   - Gerado pela execução do notebook principal
   - Contém todas as saídas das células executadas
   - Não versionado no Git (adicionado ao .gitignore)

### Resultados do Treinamento

Após o treinamento, o modelo será salvo em:
- `app/models/pipeline_aprimorado.joblib` - Modelo treinado
- `app/models/model_metadata_enhanced.json` - Metadados do modelo

## 📁 Estrutura do Projeto

```
otimizador-entrevistas/
├── app/                          # Aplicação Flask
│   ├── models/                   # Modelos treinados
│   │   ├── pipeline_aprimorado.joblib
│   │   └── model_metadata_enhanced.json
│   ├── templates/                # Templates HTML
│   │   ├── index.html
│   │   └── vaga_detalhes.html
│   ├── app.py                    # Aplicação principal
│   ├── postgresql_integration.py # Integração PostgreSQL
│   ├── requirements.txt          # Dependências Python
│   ├── .env.example             # Configurações PostgreSQL
│   └── Dockerfile               # Container da aplicação
├── data/                        # Dados fonte (JSON)
│   ├── vagas.json              # Dados das vagas
│   ├── applicants.json         # Dados dos candidatos
│   └── prospects.json          # Dados dos prospects
├── notebooks/                  # Jupyter Notebooks
│   ├── Treinamento.ipynb      # Pipeline de ML com PostgreSQL
│   └── Treinamento_executed.ipynb  # Notebook executado (auto-gerado)
├── tests/                     # Testes automatizados
│   └── test_api.py           # Testes da API
├── docker-compose.yml        # Orquestração completa
├── prometheus.yml           # Configuração Prometheus
├── nginx.conf              # Configuração Nginx
└── README.md              # Documentação
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask** 3.0.0 - Framework web
- **Gunicorn** 21.2.0 - Servidor WSGI
- **PostgreSQL** 15+ - Banco de dados principal
- **psycopg2-binary** 2.9.0 - Driver PostgreSQL
- **SQLAlchemy** 2.0.0 - ORM e abstração de banco
- **Pandas** 2.1.4 - Manipulação de dados
- **Scikit-learn** 1.3.2 - Machine Learning
- **Joblib** 1.3.2 - Serialização de modelos

### Machine Learning
- **Random Forest Classifier** - Modelo de classificação
- **TF-IDF Vectorizer** - Processamento de texto
- **One Hot Encoder** - Codificação categórica
- **Column Transformer** - Pipeline de pré-processamento
- **PostgreSQL Full-Text Search** - Busca semântica integrada

### Frontend
- **Bootstrap** 5.1.3 - Framework CSS
- **Font Awesome** 6.0.0 - Ícones
- **JavaScript** - Interatividade

### DevOps e Monitorização
- **Docker** & **Docker Compose** - Containerização
- **Nginx** - Load Balancer e Proxy Reverso
- **Prometheus** - Coleta de métricas
- **Grafana** - Visualização de métricas
- **Prometheus Flask Exporter** - Métricas da aplicação

### Testes
- **Pytest** 7.4.3 - Framework de testes
- **Coverage** - Cobertura de código

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# PostgreSQL
DB_HOST=localhost
DB_NAME=otimizador_entrevistas
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432

# Aplicação
FLASK_ENV=production
DEBUG=false
PORT=5000

# Grafana
GF_SECURITY_ADMIN_PASSWORD=admin123
GF_USERS_ALLOW_SIGN_UP=false
```

### Configuração de Produção

Para ambiente de produção com Docker:

1. **Configurar variáveis de ambiente personalizadas**:
   ```bash
   # Criar arquivo .env
   cp app/.env.example .env
   # Editar .env com configurações de produção
   ```

2. **Executar com configurações otimizadas**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Configurações recomendadas**:
   - Alterar senhas padrão do PostgreSQL
   - Configurar HTTPS com certificados
   - Configurar backup automatizado do PostgreSQL
   - Implementar log centralizado
   - Configurar replicação PostgreSQL para alta disponibilidade

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação técnica
- Verifique os logs da aplicação

---

**🎉 Desenvolvido com ❤️ usando Flask, Machine Learning e DevOps Best Practices**

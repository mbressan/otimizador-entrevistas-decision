# 🚀 Otimizador de Entrevistas com IA

Sistema de otimização de entrevistas que utiliza Machine Learning para identificar os candidatos mais compatíveis com vagas específicas, desenvolvido com Flask e Docker.

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

- **🧠 Machine Learning Otimizado**: Modelo Random Forest com 99.1% de acurácia para predição de compatibilidade candidato-vaga.
- **🌐 Interface Web Responsiva**: Dashboard intuitivo com análise de compatibilidade em tempo real.
- **🔌 API REST Simplificada**: Endpoints essenciais otimizados para integração e uso web.
- **📊 Análise Detalhada**: Score de compatibilidade com breakdown por categoria (técnica, acadêmica, idiomas).
- **📂 Gestão de Dados JSON**: Sistema eficiente e desacoplado baseado em arquivos JSON.
- **📈 Monitorização Opcional**: Prometheus e Grafana para métricas em tempo real.
- **🐳 Containerização**: Deploy completo com Docker e Docker Compose.
- **🛡️ Código Limpo**: Arquitetura refatorada e otimizada.
- **🧪 Testes Automatizados**: Suíte de testes para garantir a qualidade.

## 🏗️ Arquitetura

A arquitetura foi simplificada para focar em performance e facilidade de manutenção, utilizando uma abordagem baseada em arquivos JSON para o armazenamento de dados.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│   Flask App     │────│   Prometheus    │
│ (Load Balancer) │    │ (API + Web UI)  │    │   (Metrics)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                       │
┌──────────────────────┐   ┌─────────────────┐    ┌─────────────────┐
│  JSON Data Files     │   │ Machine Learning│    │     Grafana     │
│ (applicants.json,    │   │  Random Forest  │    │  (Dashboard)    │
│  vagas.json,         │   │ 99.1% Accuracy  │    │                 │
│  prospects.json)     │   └─────────────────┘    └─────────────────┘
└──────────────────────┘
```

### 🎯 APIs Essenciais
- **`/`** - Interface web para análise de compatibilidade.
- **`/api/predict`** - API principal para predições.
- **`/api/predict_simple`** - API otimizada para a interface web.
- **`/health`** - Health check para monitoramento.
- **`/status`** - Página de status detalhado do sistema.

## 📦 Pré-requisitos

- **Python** 3.8+
- **Docker** 20.10+ (Opcional, para execução com monitoramento)
- **Docker Compose** 2.0+ (Opcional)
- **Git**

## 🚀 Instalação e Execução

### 1. Clone o Repositório

```bash
git clone https://github.com/mbressan/otimizador-entrevistas-decision.git
cd otimizador-entrevistas-decision
```

### 2. Instale as Dependências

```bash
pip install -r app/requirements.txt
```

### 3. Execute a Aplicação

#### Modo Simples (Recomendado)
Execute o servidor Flask diretamente.

```bash
python app/app.py
```
Acesse a aplicação em: **http://localhost:5000**

#### Modo Completo com Docker (Opcional)
Utilize o Docker Compose para executar a aplicação junto com os serviços de monitoramento (Prometheus, Grafana) e o Nginx como proxy reverso.

```bash
docker-compose up --build
```
Acesse a aplicação em: **http://localhost**

## 💻 Uso da Aplicação

1.  **Acesse a interface web**: http://localhost:5000 (ou http://localhost se usar Docker).
2.  **Preencha os dados da vaga** no formulário da esquerda.
3.  **Preencha os dados do candidato** no formulário da direita.
4.  Clique em **"Analisar Compatibilidade"**.
5.  O resultado da análise, incluindo o score de compatibilidade e um detalhamento por categoria, será exibido instantaneamente.

## 🔌 API REST

### Endpoint Principal: `/api/predict`
Realiza uma predição de compatibilidade com base nos dados da vaga e do candidato.

- **Método**: `POST`
- **Payload**:
```json
{
  "vaga": {
    "titulo_vaga": "Desenvolvedor Python Sênior",
    "competencias_tecnicas_requeridas": "Python, Django, FastAPI, PostgreSQL",
    "nivel_academico": "superior",
    "nivel_ingles": "intermediário",
    "nivel_profissional": "sênior",
    "tipo_contratacao": "clt",
    "areas_atuacao": "Tecnologia"
  },
  "candidato": {
    "conhecimentos_tecnicos": "Python, Django, PostgreSQL, Docker",
    "nivel_academico": "superior",
    "nivel_ingles": "intermediário",
    "area_de_atuacao": "Desenvolvimento de Software"
  }
}
```
- **Resposta**:
```json
{
  "prediction": 1,
  "percentage": "76.4%",
  "prediction_text": "ALTA QUALIDADE",
  "quality_score": 76.44,
  "analysis": { ... }
}
```

### Outros Endpoints
-   **`/api/predict_simple`**: Versão simplificada do endpoint de predição, usada pela interface web.
-   **`/health`**: Retorna o status de saúde da aplicação e do modelo de ML.
-   **`/status`**: Exibe uma página HTML com o status detalhado dos componentes do sistema.

## 📈 Monitorização (Opcional)

Se executado com Docker, a stack inclui:
-   **Prometheus**: http://localhost:9090
-   **Grafana**: http://localhost:3000 (Login: `admin`/`admin123`)

Dashboards pré-configurados para monitorar a saúde da aplicação e a performance do modelo estão disponíveis.

## 🧪 Testes

Para executar a suíte de testes automatizados, utilize o `pytest`:

```bash
python -m pytest tests/
```

## 📁 Estrutura do Projeto

```
otimizador-entrevistas-decision/
├── app/                          # Aplicação Flask
│   ├── models/                   # Modelos de ML e metadados
│   ├── templates/                # Templates HTML (Jinja2)
│   ├── app.py                    # Lógica principal da aplicação e APIs
│   ├── postgresql_integration.py # Módulo de integração (não utilizado ativamente)
│   ├── requirements.txt          # Dependências Python
│   └── Dockerfile                # Dockerfile da aplicação
├── data/                         # Dados em formato JSON
│   ├── applicants.json
│   ├── prospects.json
│   └── vagas.json
├── notebooks/                    # Notebooks para treinamento de modelo
│   └── Treinamento.ipynb
├── tests/                        # Testes automatizados
│   └── test_api.py
├── grafana/                      # Configurações do Grafana
├── docker-compose.yml            # Orquestração de containers
├── prometheus.yml                # Configuração do Prometheus
├── nginx.conf                    # Configuração do Nginx
└── README.md                     # Documentação do projeto
```

## 🛠️ Tecnologias Utilizadas

-   **Backend**: Flask, Gunicorn
-   **Data Science**: Pandas, Scikit-learn, Joblib
-   **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
-   **DevOps**: Docker, Docker Compose, Nginx
-   **Monitoramento**: Prometheus, Grafana
-   **Testes**: Pytest

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma *issue* ou enviar um *pull request*.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

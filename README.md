# 🚀 Otimizador de Entrevistas com Machine Learning

## 🎓 Informações Acadêmicas

**Projeto**: PÓS TECH - Datathon - Machine Learning Engineering  
**Instituição**: FIAP - Faculdade de Informática e Administração Paulista  
**Fase**: 5  
**Autor**: Mateus Bressan  
**Ano**: 2025  

## 📖 Sobre o Projeto

Sistema de otimização de entrevistas que utiliza Machine Learning para identificar os candidatos mais compatíveis com vagas específicas. O projeto foi desenvolvido como entregável do Datathon de Machine Learning Engineering, implementando uma solução completa de MLOps com Flask, Docker e monitoramento em tempo real.

### 🎯 Objetivo do Datathon

Desenvolver uma solução de Machine Learning end-to-end que demonstre:
- **Engenharia de Features** para otimização de compatibilidade candidato-vaga
- **Pipeline de ML** robusto e escalável com Random Forest
- **MLOps** completo com containerização Docker
- **Monitoramento** de modelos em produção com Prometheus/Grafana
- **API REST** para integração e consumo de predições
- **Interface Web** responsiva para análise em tempo real

## 🎬 Demonstração

**Vídeo de Apresentação**: [URL_DO_VIDEO_AQUI]

## 📋 Índice

- [Informações Acadêmicas](#informações-acadêmicas)
- [Sobre o Projeto](#sobre-o-projeto)
- [Características](#características)
- [Arquitetura](#arquitetura)
- [Instalação e Execução via Docker](#instalação-e-execução-via-docker)
- [Uso da Aplicação](#uso-da-aplicação)
- [API REST](#api-rest)
- [Monitorização](#monitorização)
- [Testes](#testes)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)

## ✨ Características

- **🧠 Machine Learning Especializado**: Modelo Random Forest com 99.1% de acurácia treinado especificamente para predição de compatibilidade candidato-vaga baseado em padrões de contratações bem-sucedidas.
- **🌐 Interface Web Responsiva**: Dashboard intuitivo desenvolvido com Bootstrap 5 para análise de compatibilidade em tempo real.
- **🔌 API REST Completa**: Endpoints otimizados para integração externa e consumo interno da aplicação web.
- **📊 Análise Detalhada**: Score de compatibilidade com breakdown por categoria (técnica, acadêmica, idiomas) e justificativas detalhadas.
- **📂 Arquitetura Simplificada**: Sistema baseado em arquivos JSON para máxima portabilidade e facilidade de deploy.
- **📈 Monitorização Avançada**: Stack completa Prometheus + Grafana com métricas de ML e infraestrutura.
- **🐳 Containerização Completa**: Deploy via Docker Compose com todos os serviços orquestrados.
- **🧪 Testes Automatizados**: Suíte completa de testes via pytest e Postman com validações automáticas.
- **🚀 MLOps**: Pipeline completo de Machine Learning com monitoramento de drift e retreinamento.

## 🏗️ Arquitetura

A solução implementa uma arquitetura de MLOps completa, otimizada para performance e facilidade de manutenção, utilizando uma abordagem baseada em arquivos JSON para máxima portabilidade.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│   Flask App     │────│   Prometheus    │
│ (Load Balancer) │    │ (API + Web UI)  │    │   (Metrics)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                      │                       │
┌──────────────────────┐   ┌─────────────────┐    ┌─────────────────┐
│  JSON Data Storage   │   │ ML Pipeline     │    │     Grafana     │
│ • applicants.json    │   │ Random Forest   │    │  (Dashboards)   │
│ • vagas.json         │   │ 99.1% Accuracy  │    │ • ML Metrics    │
│ • prospects.json     │   │ • Feature Eng.  │    │ • Infrastructure│
└──────────────────────┘   │ • Preprocessing │    └─────────────────┘
                           │ • Validation    │
                           └─────────────────┘
```

### 🎯 Componentes Principais

#### **Machine Learning Engine**
- **Pipeline Completo**: Preprocessamento + Feature Engineering + Modelo
- **Modelo**: Random Forest especializado em padrões de contratação
- **Features**: 21 características otimizadas (técnicas, acadêmicas, idiomas)
- **Validação**: Cross-validation e métricas de performance contínuas

#### **API REST**
- **`/`** - Interface web para análise de compatibilidade
- **`/api/predict`** - Endpoint principal para predições ML
- **`/health`** - Health check para monitoramento
- **`/status`** - Status detalhado de todos os componentes

#### **Monitoramento MLOps**
- **Métricas de ML**: Acurácia, distribuição de scores, drift detection
- **Métricas de Sistema**: CPU, memória, latência, throughput
- **Alertas**: Degradação de performance, falhas de modelo

## � Instalação e Execução via Docker

### Pré-requisitos

- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Git**

### 1. Clone o Repositório

```bash
git clone https://github.com/mbressan/otimizador-entrevistas-decision.git
cd otimizador-entrevistas-decision
```

### 2. Execução Completa (Recomendado)

O projeto foi projetado para execução principal via Docker, incluindo toda a stack de monitoramento:

```bash
# Executar toda a stack
docker-compose up --build

# Executar em background
docker-compose up -d --build
```

**Serviços Disponíveis**:
- **Aplicação Principal**: http://localhost *(via Nginx)*
- **API Direta**: http://localhost:5000 *(Flask app)*
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 *(admin/admin123)*

### 3. Execução Simples (Desenvolvimento)

Para desenvolvimento local sem monitoramento:

```bash
# Instalar dependências
pip install -r app/requirements.txt

# Executar aplicação Flask
python app/app.py
```

**Acesso**: http://localhost:5000

### 4. Validação do Deploy

```bash
# Verificar status dos containers
docker-compose ps

# Testar health check
curl http://localhost/health

# Testar predição via API
curl -X POST http://localhost/api/predict \
  -H "Content-Type: application/json" \
  -d '{"vaga": {"titulo_vaga": "Desenvolvedor Python"}, "candidato": {"conhecimentos_tecnicos": "Python"}}'
```

## 💻 Uso da Aplicação

### Interface Web

1. **Acesse a aplicação**: http://localhost *(Docker)* ou http://localhost:5000 *(local)*
2. **Preencha os dados da vaga** no formulário da esquerda:
   - Título da vaga
   - Competências técnicas requeridas
   - Nível acadêmico, profissional e inglês
   - Tipo de contratação e área de atuação
3. **Preencha os dados do candidato** no formulário da direita:
   - Conhecimentos técnicos
   - Nível acadêmico, inglês e área de atuação
4. **Clique em "Analisar Compatibilidade"**
5. **Visualize o resultado**:
   - Score de compatibilidade (0-100%)
   - Classificação (Alta/Baixa Qualidade)
   - Análise detalhada por categoria
   - Justificativas e recomendações

### Interpretação dos Resultados

#### Scores de Compatibilidade
- **80-100%**: **Alta Qualidade** - Candidato altamente compatível
- **60-79%**: **Qualidade Moderada** - Boa compatibilidade com gaps menores
- **40-59%**: **Qualidade Média** - Compatibilidade parcial
- **0-39%**: **Baixa Qualidade** - Pouca compatibilidade

#### Análise Detalhada
- **Compatibilidade Técnica**: Match entre competências requeridas e conhecimentos
- **Compatibilidade Acadêmica**: Alinhamento de formação
- **Compatibilidade de Idiomas**: Nível de inglês adequado
- **Match de Área**: Experiência na área de atuação
- **Tipo de Contrato**: Alinhamento com preferências

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

## 📈 Monitorização

A solução inclui uma stack completa de monitoramento MLOps para acompanhar tanto a performance da aplicação quanto a qualidade do modelo de ML.

### Serviços de Monitoramento

#### **Prometheus** (http://localhost:9090)
- Coleta de métricas em tempo real
- Métricas de ML: predições, distribuição de scores, acurácia
- Métricas de sistema: CPU, memória, latência, throughput

#### **Grafana** (http://localhost:3000)
**Login**: `admin` / `admin123`

**Dashboards Disponíveis**:
- **Main Dashboard**: Métricas de ML e aplicação
  - Volume de predições por minuto
  - Distribuição de scores de qualidade
  - Latência média das predições
  - Taxa de sucesso/erro
- **Infrastructure Dashboard**: Métricas de infraestrutura
  - CPU e memória do sistema
  - Uso de disco e rede
  - Status dos containers Docker

### Métricas Principais

#### **Machine Learning**
- `hired_model_predictions_total`: Total de predições realizadas
- `quality_score_histogram`: Distribuição dos scores de qualidade
- `hired_model_accuracy`: Acurácia atual do modelo
- `prediction_latency_seconds`: Tempo de resposta das predições

#### **Aplicação**
- `flask_http_request_duration_seconds`: Latência dos endpoints
- `flask_http_request_total`: Volume de requisições
- `flask_http_request_exceptions_total`: Taxa de erros

#### **Sistema**
- `node_cpu_seconds_total`: Uso de CPU
- `node_memory_MemAvailable_bytes`: Memória disponível
- `node_disk_io_time_seconds_total`: I/O de disco
- `node_network_receive_bytes_total`: Tráfego de rede

## 🧪 Testes

O projeto inclui uma suíte completa de testes automatizados para garantir a qualidade e confiabilidade da solução.

### Testes Python (pytest)

```bash
# Executar todos os testes
python -m pytest tests/ -v

# Executar com coverage
python -m pytest tests/ --cov=app --cov-report=html

# Executar testes específicos
python -m pytest tests/test_api.py::test_predict_endpoint -v
```

**Cobertura**: 80%+ de coverage em componentes críticos

### Testes de API (Postman)

Uma coleção completa de testes está disponível no diretório `postman/`:

```bash
# Instalar Newman (CLI do Postman)
npm install -g newman

# Executar collection completa
newman run postman/otimizador-entrevistas.postman_collection.json \
  -e postman/otimizador-entrevistas.postman_environment.json

# Executar com relatório HTML
newman run postman/otimizador-entrevistas.postman_collection.json \
  -e postman/otimizador-entrevistas.postman_environment.json \
  --reporters cli,htmlextra \
  --reporter-htmlextra-export report.html
```

#### Cenários de Teste Postman
- **Health Check**: Verificação de disponibilidade
- **ML Predictions**: Testes de predição com diferentes cenários
- **High Quality Match**: Candidato ideal para vaga sênior
- **Low Quality Match**: Candidato inadequado
- **Error Handling**: Validação de tratamento de erros
- **Response Structure**: Validação de schema de resposta
- **Performance Tests**: Verificação de tempo de resposta

### Validações Automáticas
- ✅ Status codes (200, 400, 500)
- ✅ Tempo de resposta (< 2000ms)
- ✅ Estrutura de resposta JSON
- ✅ Tipos de dados e ranges válidos
- ✅ Lógica de negócio e consistência

## 📁 Estrutura do Projeto

```
otimizador-entrevistas-decision/
├── app/                          # 🐍 Aplicação Flask Principal
│   ├── models/                   #   📊 Modelos ML e metadados
│   │   ├── pipeline_aprimorado.joblib      # Modelo Random Forest treinado
│   │   └── model_metadata_enhanced.json   # Metadados do modelo
│   ├── templates/                #   🌐 Templates HTML (Jinja2)
│   │   ├── index.html           #     Interface principal
│   │   ├── status.html          #     Página de status
│   │   └── vaga_detalhes.html   #     Detalhes de vaga
│   ├── app.py                    #   🚀 Aplicação Flask e APIs
│   ├── requirements.txt          #   📦 Dependências Python
│   └── Dockerfile                #   🐳 Container da aplicação
│
├── data/                         # 📄 Dados em Formato JSON
│   ├── applicants.json          #   👥 Dados de candidatos
│   ├── prospects.json           #   📈 Histórico de prospecções
│   ├── vagas.json               #   💼 Dados de vagas
│   └── READ.ME.txt              #   📖 Documentação dos dados
│
├── notebooks/                    # 📓 Jupyter Notebooks
│   └── Treinamento.ipynb        #   🤖 Notebook de treinamento ML
│
├── tests/                        # 🧪 Testes Automatizados
│   └── test_api.py               #   ✅ Testes da API REST
│
├── postman/                      # 📮 Testes Postman
│   ├── otimizador-entrevistas.postman_collection.json  # Collection principal
│   ├── otimizador-entrevistas.postman_environment.json # Variáveis ambiente
│   ├── examples/                 #   📋 Cenários de teste
│   ├── README.md                 #   📖 Documentação dos testes
│   └── TEST_SCENARIOS.md         #   🎯 Manual de cenários
│
├── grafana/                      # 📊 Configurações Grafana
│   ├── dashboards/               #   📈 Dashboards pré-configurados
│   │   ├── main-dashboard.json           # Dashboard ML
│   │   └── infrastructure-dashboard.json # Dashboard infraestrutura
│   └── provisioning/             #   ⚙️ Configurações automáticas
│
├── scripts/                      # 🔧 Scripts de Automação
│   └── download-data.sh          #   💾 Download de dados
│
├── docker-compose.yml            # 🐳 Orquestração de containers
├── prometheus.yml                # 📊 Configuração Prometheus
├── nginx.conf                    # 🌐 Configuração Nginx
└── README.md                     # 📖 Documentação principal
```

### Componentes Principais

#### **Machine Learning Pipeline**
- **Modelo**: Random Forest com 99.1% de acurácia
- **Features**: 21 características otimizadas
- **Target**: Padrões de candidatos contratados com sucesso
- **Pipeline**: Preprocessamento + Feature Engineering + Predição

#### **API e Interface**
- **Flask App**: API REST e interface web responsiva
- **Endpoints**: Predição, health check, status
- **Templates**: Bootstrap 5 com JavaScript vanilla

#### **Monitoramento MLOps**
- **Prometheus**: Coleta de métricas ML e sistema
- **Grafana**: Dashboards especializados
- **Alertas**: Degradação de performance e falhas

## 🛠️ Tecnologias Utilizadas

### **Machine Learning & Data Science**
- **scikit-learn 1.3.2**: Pipeline de ML, Random Forest, preprocessamento
- **pandas 2.1.4**: Manipulação e análise de dados
- **numpy**: Computação numérica
- **joblib 1.3.2**: Serialização de modelos ML

### **Backend & API**
- **Flask 3.0.0**: Framework web e API REST
- **Gunicorn**: Servidor WSGI para produção
- **prometheus-flask-exporter 0.23.0**: Métricas de aplicação

### **Frontend & Interface**
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript (Vanilla)**: Interações do frontend
- **Jinja2**: Template engine do Flask
- **HTML5/CSS3**: Estrutura e estilos

### **DevOps & Containerização**
- **Docker**: Containerização da aplicação
- **Docker Compose**: Orquestração de múltiplos serviços
- **Nginx**: Proxy reverso e load balancing

### **Monitoramento & Observabilidade**
- **Prometheus**: Coleta de métricas
- **Grafana**: Dashboards e visualizações
- **node-exporter**: Métricas de sistema
- **cAdvisor**: Métricas de containers

### **Testes & Qualidade**
- **pytest 7.4.3**: Framework de testes Python
- **Postman/Newman**: Testes de API
- **Coverage**: Análise de cobertura de código

### **Arquitetura de Dados**
- **JSON**: Armazenamento de dados (portabilidade)
- **Git LFS**: Versionamento de arquivos grandes
- **Pandas DataFrames**: Processamento em memória

## 🚀 Próximos Passos

### Melhorias Futuras
- **Retreinamento Automático**: Pipeline de CI/CD para atualização do modelo
- **A/B Testing**: Comparação de diferentes versões do modelo
- **Feature Store**: Centralização de features para reutilização
- **Real-time Inference**: API de predição em tempo real via streaming

### Escalabilidade
- **Kubernetes**: Deploy em cluster para alta disponibilidade
- **Redis**: Cache de predições frequentes
- **PostgreSQL**: Migração para banco relacional em produção
- **Apache Kafka**: Stream processing para dados em tempo real

## 👨‍💻 Autor

**Mateus Bressan**  
Pós-graduando em Machine Learning Engineering - FIAP  
📧 [email@exemplo.com]  
💼 [LinkedIn](https://linkedin.com/in/mateus-bressan)  
🐙 [GitHub](https://github.com/mbressan)  

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**🎓 Projeto desenvolvido como entregável do Datathon de Machine Learning Engineering da FIAP - Fase 5**

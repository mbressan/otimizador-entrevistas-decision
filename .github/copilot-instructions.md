<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Instruções Específicas do Projeto - Otimizador de Entrevistas

## Contexto do Projeto
Este é um sistema de otimização de entrevistas que utiliza Machine Learning para identificar candidatos mais compatíveis com vagas específicas. O projeto é desenvolvido em Python com Flask, utiliza scikit-learn para ML, e inclui containerização Docker com monitorização Prometheus/Grafana.

## Estrutura de Dados
- **Vagas**: JSON com informações básicas, perfil da vaga, competências técnicas
- **Candidatos**: JSON com informações pessoais, formação acadêmica, experiência profissional
- **Prospects**: JSON com histórico de candidaturas e situações (usado para criar variável alvo)

## Padrões de Código

### Machine Learning
- Usar sklearn Pipeline para combinar pré-processamento e modelo
- TfidfVectorizer para features de texto (competências)
- OneHotEncoder para features categóricas
- RandomForestClassifier como modelo principal
- Sempre salvar modelos com joblib no diretório app/models/

### Flask Application
- Usar blueprint pattern para organizar rotas
- Implementar error handling adequado
- Incluir logging estruturado
- Validar dados de entrada na API
- Usar Jinja2 templates com Bootstrap para UI

### Data Processing
- Normalizar dados JSON para DataFrames pandas
- Tratar valores nulos com fillna('')
- Padronizar strings (lower, strip)
- Combinar features de texto relevantes

### Containerização
- Usar Python 3.12-slim como base
- Multi-stage builds quando necessário
- Usuário não-root para segurança
- Health checks obrigatórios
- Volumes para dados e modelos

### Testes
- pytest para testes unitários e integração
- Mockar dependências externas
- Testar funções de processamento de dados
- Validar endpoints da API
- Coverage mínima de 80%

## Convenções de Nomenclatura
- **Variáveis**: snake_case
- **Funções**: snake_case
- **Classes**: PascalCase
- **Constantes**: UPPER_CASE
- **Arquivos**: lowercase com hífens

## Dependências Principais
- flask==3.0.0
- pandas==2.1.4
- scikit-learn==1.3.2
- joblib==1.3.2
- prometheus-flask-exporter==0.23.0
- pytest==7.4.3

## Monitorização
- Usar prometheus_flask_exporter para métricas automáticas
- Implementar health check endpoint
- Logs estruturados em JSON
- Métricas customizadas para ML model performance

## Segurança
- Nunca hardcode credenciais
- Usar variáveis de ambiente
- Validar entradas do usuário
- Implementar rate limiting em produção
- HTTPS obrigatório em produção

## Performance
- Cache de modelos ML em memória
- Otimizar queries de dados
- Usar gunicorn com múltiplos workers
- Implementar pagination para listas grandes

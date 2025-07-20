# 🚀 Guia de Deploy em Produção - Otimizador de Entrevistas

## 📋 Resumo da Implementação

Todos os **4 próximos passos** do notebook foram implementados com sucesso:

✅ **1. Integração do modelo na aplicação principal**
- Modelo carregado automaticamente no `app.py`
- Função `prepare_hired_candidates_features()` implementada
- Metadados do modelo carregados para validação

✅ **2. Endpoints para predições**
- `/api/predict_hired_quality` - Predição de qualidade
- `/api/predict_hired_auto` - Predição automática
- `/api/analyze_candidate_quality` - Análise detalhada
- `/api/model_health` - Saúde do modelo
- `/api/retrain_model` - Retreinamento

✅ **3. Monitoramento de performance**
- Métricas Prometheus integradas
- Dashboard Grafana configurado
- Logs estruturados
- Alertas automáticos

✅ **4. Retreinamento periódico**
- Script automático de retreinamento
- Agendamento via cron
- Validação de qualidade
- Backup de modelos

## 🛠️ Instalação e Configuração

### 1. Configuração Rápida (Desenvolvimento)

```bash
# Navegar para o projeto
cd /home/mateus/otimizador-entrevistas-decision

# Instalar dependências
pip install -r app/requirements.txt

# Iniciar aplicação
python app/app.py
```

### 2. Configuração Completa (Produção)

```bash
# Executar script de configuração
sudo bash scripts/setup_production.sh

# Iniciar serviços
sudo systemctl start ml-optimizer
sudo systemctl start prometheus

# Verificar status
sudo systemctl status ml-optimizer
```

## 📊 URLs e Endpoints

### Aplicação Principal
- **API Base**: `http://localhost:5000`
- **Interface Web**: `http://localhost:5000`
- **Status**: `http://localhost:5000/status`

### Novos Endpoints ML
- **Predição de Qualidade**: `POST /api/predict_hired_quality`
- **Predição Automática**: `POST /api/predict_hired_auto`
- **Análise Detalhada**: `POST /api/analyze_candidate_quality`
- **Saúde do Modelo**: `GET /api/model_health`
- **Retreinamento**: `POST /api/retrain_model`

### Monitoramento
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`

## 🔧 Configuração dos Serviços

### Retreinamento Automático

O script `scripts/auto_retrain.sh` executa verificações automáticas:

```bash
# Configurar cron (executar uma vez)
crontab -e

# Adicionar linha:
0 2 * * * /home/mateus/otimizador-entrevistas-decision/scripts/auto_retrain.sh
```

### Monitoramento Prometheus

Métricas coletadas automaticamente:
- `hired_model_predictions_total` - Total de predições
- `quality_score_distribution` - Distribuição de scores
- `model_accuracy_current` - Acurácia atual
- `model_age_days` - Idade do modelo
- `new_data_available_count` - Dados disponíveis

### Logs do Sistema

```bash
# Logs da aplicação
tail -f /var/log/ml-optimizer/error.log

# Logs do retreinamento
tail -f /var/log/model_retrain.log

# Logs do sistema
journalctl -u ml-optimizer -f
```

## 📋 Checklist de Produção

### Antes do Deploy
- [ ] Backup do banco de dados
- [ ] Teste dos endpoints em staging
- [ ] Configuração do monitoramento
- [ ] Validação do modelo treinado

### Após o Deploy
- [ ] Verificar carregamento do modelo
- [ ] Testar endpoints de predição
- [ ] Configurar alertas do Grafana
- [ ] Agendar retreinamento automático

### Monitoramento Contínuo
- [ ] Verificar métricas Prometheus
- [ ] Analisar logs de erro
- [ ] Monitorar acurácia do modelo
- [ ] Validar retreinamento automático

## 🎯 Características do Modelo em Produção

### Modelo Atual
- **Arquivo**: `models/pipeline_candidatos_contratados.joblib`
- **Acurácia**: 99.1%
- **Dados de Treinamento**: 7.857 candidatos contratados
- **Features**: 21 características otimizadas

### Critérios de Retreinamento
- **Idade Máxima**: 90 dias
- **Novos Dados**: > 500 registros
- **Acurácia Mínima**: 85%
- **Verificação**: Diária às 2:00 AM

## 🚨 Troubleshooting

### Problemas Comuns

**Modelo não carrega**
```bash
# Verificar arquivo do modelo
ls -la app/models/pipeline_candidatos_contratados.joblib

# Verificar logs
journalctl -u ml-optimizer --since "1 hour ago"
```

**Predições com erro**
```bash
# Testar endpoint
curl -X POST http://localhost:5000/api/model_health

# Verificar formato dos dados
curl -X POST http://localhost:5000/api/predict_hired_quality \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": 1}'
```

**Retreinamento falha**
```bash
# Executar manualmente
bash scripts/auto_retrain.sh

# Verificar dados de treinamento
python -c "import pandas as pd; print(pd.read_json('data/prospects.json').info())"
```

## 📈 Métricas de Sucesso

### KPIs Técnicos
- **Uptime**: > 99.5%
- **Latência**: < 200ms por predição
- **Acurácia**: > 95%
- **Taxa de Erro**: < 1%

### KPIs de Negócio
- **Qualidade das Contratações**: Melhoria na avaliação
- **Tempo de Decisão**: Redução no processo
- **ROI do Modelo**: Custo vs. benefício

## 🔄 Processo de Atualização

### Atualização do Código
```bash
git pull origin main
sudo systemctl restart ml-optimizer
```

### Atualização do Modelo
```bash
# Retreinamento manual
curl -X POST http://localhost:5000/api/retrain_model \
  -H "Content-Type: application/json" \
  -d '{"force": true}'
```

### Backup e Restore
```bash
# Backup do modelo
cp app/models/pipeline_candidatos_contratados.joblib backup/

# Restore se necessário
cp backup/pipeline_candidatos_contratados.joblib app/models/
sudo systemctl restart ml-optimizer
```

## 📞 Suporte

Para problemas técnicos:
1. Verificar logs em `/var/log/ml-optimizer/`
2. Consultar métricas no Prometheus
3. Executar health check: `GET /api/model_health`
4. Revisar documentação em `API_ENDPOINTS.md`

---

**🎉 Sistema de ML em produção configurado com sucesso!**

Todas as funcionalidades implementadas:
- ✅ Modelo integrado
- ✅ 5 endpoints de predição
- ✅ Monitoramento completo
- ✅ Retreinamento automático
- ✅ Documentação abrangente

# 🚀 Testando os Dashboards do Grafana

## 📋 Passo a Passo para Verificar os Dashboards

### 1. Iniciar os Serviços
```bash
# Parar containers existentes (se houver)
docker-compose down

# Iniciar toda a stack
docker-compose up --build -d

# Verificar status dos containers
docker-compose ps
```

### 2. Aguardar Inicialização
```bash
# Verificar logs do Grafana
docker-compose logs -f grafana

# Aguardar até ver a mensagem: "HTTP Server Listen"
# Pressionar Ctrl+C para sair dos logs
```

### 3. Acessar o Grafana
- **URL**: http://localhost:3000
- **Login**: admin
- **Senha**: admin123

### 4. Verificar Dashboards Automáticos

Ao fazer login, você deve ver:

1. **Dashboard Principal** (`Otimizador de Entrevistas - Dashboard Principal`):
   - Taxa de Requisições (req/s)
   - Tempo de Resposta (95th percentile)
   - Total de Requisições por Endpoint
   - Taxa de Sucesso (%)
   - Predições de ML (última hora)
   - Tempo de Resposta das Predições ML

2. **Dashboard de Infraestrutura** (`Otimizador de Entrevistas - Infraestrutura`):
   - Status dos Containers (Flask, PostgreSQL, Prometheus, Nginx)
   - Conexões PostgreSQL
   - Transações PostgreSQL
   - Uso de Memória por Container
   - Uso de CPU por Container

### 5. Gerar Métricas para Teste

```bash
# Fazer algumas requisições para gerar dados
curl http://localhost/health
curl http://localhost/api/vagas
curl http://localhost/api/candidatos

# Fazer predição de ML
curl -X POST http://localhost/api/predict \
  -H "Content-Type: application/json" \
  -d '{"competencias_combinadas": "python flask", "nivel_profissional": "senior"}'
```

### 6. Verificar Métricas no Prometheus

- **URL**: http://localhost:9090
- **Consultas para testar**:
  - `flask_http_request_total`
  - `flask_http_request_duration_seconds`
  - `up{job="flask-app"}`

## 🔧 Troubleshooting

### Dashboard não aparece:
```bash
# Verificar volumes do Grafana
docker volume ls | grep grafana

# Verificar configuração
docker-compose exec grafana ls -la /etc/grafana/provisioning/
docker-compose exec grafana ls -la /var/lib/grafana/dashboards/
```

### Métricas não aparecem:
```bash
# Verificar se o Prometheus está coletando métricas
curl http://localhost:9090/api/v1/targets

# Verificar métricas da aplicação
curl http://localhost:5000/metrics
```

### Reiniciar serviços:
```bash
# Reiniciar apenas o Grafana
docker-compose restart grafana

# Reiniciar toda a stack
docker-compose restart
```

## ✅ Verificação de Sucesso

Os dashboards estão funcionando corretamente quando:

1. **Login automático** no Grafana com admin/admin123
2. **Dois dashboards** visíveis na lista
3. **Prometheus configurado** como datasource automaticamente
4. **Métricas aparecem** nos gráficos após fazer algumas requisições
5. **Status dos containers** aparece como "UP" (verde)

## 📊 Dashboards Esperados

### Dashboard Principal
- ✅ Taxa de Requisições em tempo real
- ✅ Tempo de resposta (P95)
- ✅ Contadores de requisições por endpoint
- ✅ Taxa de sucesso das requisições
- ✅ Métricas específicas de ML

### Dashboard de Infraestrutura  
- ✅ Status visual dos 4 containers principais
- ✅ Métricas de conexões PostgreSQL
- ✅ Uso de recursos por container
- ✅ Transações de banco de dados

Se todos os itens acima estiverem funcionando, os dashboards foram configurados com sucesso! 🎉

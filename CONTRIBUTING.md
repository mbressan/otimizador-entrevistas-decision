# 🤝 Contribuindo para o Otimizador de Entrevistas

Obrigado por seu interesse em contribuir! Este documento fornece diretrizes para contribuições.

## 📋 Como Contribuir

### 1. Fork e Clone
```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/SEU_USERNAME/otimizador-entrevistas.git
cd otimizador-entrevistas
```

### 2. Configure o Ambiente
```bash
# Execute via Docker (recomendado)
docker-compose up --build

# Acesse os serviços:
# - Aplicação: http://localhost
# - Grafana: http://localhost:3000 (admin/admin123)
# - Prometheus: http://localhost:9090

# Ou configure ambiente local
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r app/requirements.txt
```

### 3. Crie uma Branch
```bash
git checkout -b feature/sua-funcionalidade
# ou
git checkout -b fix/seu-bugfix
```

### 4. Desenvolva e Teste
```bash
# Execute os testes
docker-compose exec app python -m pytest tests/ -v

# Ou localmente
pytest tests/ -v
```

### 5. Commit e Push
```bash
git add .
git commit -m "feat: adiciona nova funcionalidade X"
git push origin feature/sua-funcionalidade
```

### 6. Abra um Pull Request
- Descreva claramente as mudanças
- Referencie issues relacionadas
- Inclua capturas de tela se aplicável

## 🎯 Tipos de Contribuição

### 🐛 Correção de Bugs
- Documente o bug claramente
- Inclua passos para reproduzir
- Adicione testes para prevenir regressão

### ✨ Novas Funcionalidades
- Discuta a funcionalidade em uma issue primeiro
- Mantenha compatibilidade com versões anteriores
- Adicione documentação adequada

### 📚 Documentação
- Melhore README.md
- Adicione comentários no código
- Crie tutoriais ou guias

### 🧪 Testes
- Aumente cobertura de testes
- Adicione testes de integração
- Melhore testes existentes

## 📝 Padrões de Código

### Python
- Siga PEP 8
- Use type hints quando possível
- Documente funções complexas
- Mantenha funções pequenas e focadas

### Machine Learning
- Use sklearn Pipeline para pré-processamento
- Documente features e métricas
- Versionize modelos adequadamente
- Inclua validação de dados

### Docker
- Use multi-stage builds quando necessário
- Otimize tamanho das imagens
- Inclua health checks
- Documente variáveis de ambiente

## 🧪 Executando Testes

### Testes Unitários
```bash
# Via Docker
docker-compose exec app python -m pytest tests/test_api.py -v

# Local
pytest tests/test_api.py -v
```

### Testes de Integração
```bash
# Testar toda a stack
docker-compose up -d
curl http://localhost/health
```

### Testes de Performance
```bash
# Verificar tempo de resposta da API
time curl http://localhost/api/predict -X POST -H "Content-Type: application/json" -d '{"competencias_combinadas":"python", "nivel_profissional":"senior"}'
```

## 📊 Machine Learning

### Adicionando Novas Features
1. Modifique função `prepare_enhanced_features()`
2. Atualize pipeline de pré-processamento
3. Re-treine o modelo no notebook
4. Teste com dados de validação

### Novos Modelos
1. Adicione no notebook `Treinamento.ipynb`
2. Compare métricas com modelo atual
3. Documente melhorias
4. Teste em ambiente de produção

## 📈 Monitorização e Observabilidade

### Grafana Dashboards
- **Dashboard Principal**: Métricas da aplicação, ML e performance
- **Dashboard de Infraestrutura**: Status dos containers e recursos do sistema
- **Acesso**: http://localhost:3000 (admin/admin123)

### Prometheus Métricas
- **Flask App**: Requisições, tempo de resposta, status codes
- **Aplicação**: http://localhost:5000/metrics
- **Prometheus UI**: http://localhost:9090

### Adicionando Novas Métricas
1. Use `prometheus_flask_exporter` para métricas automáticas
2. Adicione métricas customizadas com `Counter`, `Histogram`, `Gauge`
3. Configure alertas no Prometheus (opcional)
4. Atualize dashboards do Grafana

### Logs e Debugging
```bash
# Ver logs em tempo real
docker-compose logs -f app
docker-compose logs -f postgresql
docker-compose logs -f grafana

# Verificar status dos containers
docker-compose ps
```

## 🐳 Docker e Infraestrutura

### Novos Serviços
1. Adicione ao `docker-compose.yml`
2. Configure health checks
3. Documente no README
4. Teste integração completa

### Configurações
1. Use variáveis de ambiente
2. Documente no `.env.example`
3. Mantenha defaults seguros
4. Teste diferentes configurações

## 📋 Convenções

### Commits
Use [Conventional Commits](https://conventionalcommits.org/):
- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` documentação
- `style:` formatação
- `refactor:` refatoração
- `test:` testes
- `chore:` manutenção

### Issues
- Use templates quando disponíveis
- Seja específico no título
- Inclua passos para reproduzir (bugs)
- Adicione labels apropriadas

### Pull Requests
- Título claro e descritivo
- Descrição detalhada das mudanças
- Referencie issues relacionadas
- Inclua capturas de tela se aplicável

## ❓ Dúvidas?

- Abra uma issue com tag `question`
- Consulte a documentação no README
- Verifique issues existentes

## 🎉 Reconhecimento

Contribuidores são listados no README.md. Obrigado por ajudar a melhorar o projeto!

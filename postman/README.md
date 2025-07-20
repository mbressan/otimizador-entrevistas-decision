# Testes Postman - Otimizador de Entrevistas

Esta pasta contém as coleções e ambientes do Postman para testar a API do Otimizador de Entrevistas.

## Estrutura dos Arquivos

- `otimizador-entrevistas.postman_collection.json` - Coleção principal com todos os testes da API
- `otimizador-entrevistas.postman_environment.json` - Ambiente de desenvolvimento
- `examples/` - Pasta com exemplos de dados para testes

## Como Usar

### 1. Importar no Postman

1. Abra o Postman
2. Clique em "Import"
3. Selecione os arquivos da collection e environment
4. Configure o ambiente como ativo

### 2. Executar Testes

#### Testes Individuais
- Selecione uma requisição e clique "Send"
- Verifique os resultados nos testes automáticos

#### Executar Toda a Coleção
```bash
# Via Newman (CLI do Postman)
npm install -g newman
newman run otimizador-entrevistas.postman_collection.json -e otimizador-entrevistas.postman_environment.json
```

## Endpoints Testados

### ✅ Health Check
- `GET /health` - Verifica se a aplicação está funcionando

### ✅ Status da Aplicação
- `GET /status` - Página de status com informações do sistema

### ✅ Predições de ML
- `POST /api/predict` - Endpoint principal para predições
  - Testa formato completo (vaga + candidato)
  - Testa formato direto (features)
  - Testa validação de campos obrigatórios
  - Testa casos de erro

## Casos de Teste Cobertos

### Casos de Sucesso
1. **Predição Alta Qualidade** - Candidato com match perfeito
2. **Predição Baixa Qualidade** - Candidato com pouco match
3. **Predição Formato Direto** - Usando features preparadas

### Casos de Erro
1. **Dados Ausentes** - Requisição sem vaga ou candidato
2. **Campos Obrigatórios** - Validação de campos necessários
3. **Formato Inválido** - JSON malformado

### Validações Automáticas
- Status codes corretos (200, 400, 500)
- Estrutura da resposta JSON
- Presença de campos obrigatórios
- Tipos de dados corretos
- Valores dentro de ranges esperados

## Dados de Teste

Os exemplos incluem diferentes cenários:
- Desenvolvedor Python Sênior vs vaga Python
- Desenvolvedor Junior vs vaga Sênior
- Profissional de outra área vs vaga de TI
- Diferentes tipos de contratação (CLT, PJ)
- Diferentes níveis de inglês e acadêmicos

## Executar via CI/CD

```yaml
# Exemplo para GitHub Actions
- name: Run Postman Tests
  run: |
    npm install -g newman
    newman run postman/otimizador-entrevistas.postman_collection.json \
      -e postman/otimizador-entrevistas.postman_environment.json \
      --reporters cli,json \
      --reporter-json-export results.json
```

## Métricas Monitoradas

Os testes também verificam se as métricas Prometheus estão sendo geradas:
- `hired_model_predictions_total`
- `hired_model_quality_scores`
- `flask_http_request_duration_seconds`
- `flask_http_request_total`

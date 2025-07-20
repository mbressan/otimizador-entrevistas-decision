# Manual de Execução dos Testes Postman

## Cenários de Teste Disponíveis

### 1. **high-quality-match.json**
- **Descrição**: Candidato experiente com competências que se alinham perfeitamente com uma vaga sênior
- **Expectativa**: Alta qualidade (prediction 1, quality_score > 80)
- **Uso**: Teste de cenário ideal de compatibilidade

### 2. **low-quality-match.json**
- **Descrição**: Candidato júnior com competências limitadas para vaga que exige experiência
- **Expectativa**: Baixa qualidade (prediction 0, quality_score < 50)
- **Uso**: Teste de cenário de baixa compatibilidade

### 3. **frontend-match.json**
- **Descrição**: Candidato especializado em frontend para vaga de desenvolvimento frontend
- **Expectativa**: Qualidade moderada a alta (prediction variável, quality_score 60-85)
- **Uso**: Teste de compatibilidade específica de área

### 4. **junior-match.json**
- **Descrição**: Candidato júnior adequado para vaga júnior
- **Expectativa**: Qualidade média (prediction variável, quality_score 50-70)
- **Uso**: Teste de alinhamento de nível profissional

### 5. **overqualified-mismatch.json**
- **Descrição**: Candidato super qualificado para vaga básica (estagiário)
- **Expectativa**: Qualidade variável (pode ser baixa por over-qualification)
- **Uso**: Teste de incompatibilidade por super qualificação

### 6. **incompatible-mismatch.json**
- **Descrição**: Candidato de área completamente diferente sem competências técnicas
- **Expectativa**: Baixa qualidade (prediction 0, quality_score baixo)
- **Uso**: Teste de incompatibilidade total

## Como Executar

### Opção 1: Interface Postman
1. Importe a collection `otimizador-entrevistas.postman_collection.json`
2. Importe o environment `otimizador-entrevistas.postman_environment.json`
3. Execute cada teste individualmente ou toda a collection

### Opção 2: Newman CLI
```bash
# Instalar Newman
npm install -g newman

# Executar toda a collection
newman run otimizador-entrevistas.postman_collection.json \
  -e otimizador-entrevistas.postman_environment.json \
  --reporters cli,json \
  --reporter-json-export results.json

# Executar com dados específicos de exemplo
newman run otimizador-entrevistas.postman_collection.json \
  -e otimizador-entrevistas.postman_environment.json \
  -d examples/high-quality-match.json
```

### Opção 3: Testes Personalizados
Para criar seus próprios testes:

1. Copie um dos arquivos de exemplo
2. Modifique os campos `vaga` e `candidato` conforme necessário
3. Ajuste a `expected_result` baseada no cenário
4. Execute via Newman ou Postman

## Validações Automáticas

Cada teste inclui:
- ✅ **Status Code**: Verifica se retorna 200
- ✅ **Response Time**: Confirma resposta em < 2000ms
- ✅ **Content-Type**: Valida header JSON
- ✅ **Schema**: Verifica estrutura da resposta
- ✅ **Required Fields**: Confirma presença de campos obrigatórios
- ✅ **Data Types**: Valida tipos de dados (números, strings, etc.)
- ✅ **Business Logic**: Verifica lógica específica (ranges, valores válidos)

## Interpretação dos Resultados

### Campos de Resposta
- **`prediction`**: 0 (baixa compatibilidade) ou 1 (alta compatibilidade)
- **`quality_score`**: Score de 0-100 indicando qualidade da compatibilidade
- **`match_details`**: Detalhes sobre competências encontradas/faltantes
- **`prediction_confidence`**: Nível de confiança do modelo (0-1)

### Cenários de Sucesso
- **Alta Qualidade**: prediction=1, quality_score > 80
- **Média Qualidade**: quality_score 50-80
- **Baixa Qualidade**: prediction=0, quality_score < 50

### Troubleshooting
Se algum teste falhar:
1. Verifique se a aplicação está rodando (http://localhost:5000)
2. Confirme se o modelo ML está carregado corretamente
3. Valide os dados de entrada no formato JSON esperado
4. Consulte os logs da aplicação para erros específicos

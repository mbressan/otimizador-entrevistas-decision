# 📊 Guia de Gestão de Dados para Deploy

## 🎯 Estratégias para Arquivos de Dados Grandes

### 1. 🔧 Git LFS (Large File Storage) - ✅ CONFIGURADO

**Vantagens:**
- Mantém arquivos no repositório Git
- Versionamento e histórico
- Download automático no clone

**Uso:**
```bash
# Já configurado! Os arquivos são baixados automaticamente
git clone https://github.com/mbressan/otimizador-entrevistas-decision.git
cd otimizador-entrevistas-decision
git lfs pull  # Baixa arquivos LFS
./scripts/deploy.sh
```

### 2. 🌐 Download Automático via Script

**Para ambientes onde Git LFS não é viável:**

```bash
# Criar script de download dos dados
# scripts/download-data.sh

#!/bin/bash
echo "📥 Baixando dados de treinamento..."

# Exemplo: Baixar de servidor/storage
curl -o data/applicants.json "https://seu-servidor.com/data/applicants.json"
curl -o data/vagas.json "https://seu-servidor.com/data/vagas.json" 
curl -o data/prospects.json "https://seu-servidor.com/data/prospects.json"

echo "✅ Dados baixados com sucesso!"
```

### 3. ☁️ Armazenamento em Nuvem

**AWS S3 / Google Cloud Storage / Azure Blob:**

```bash
# Exemplo com AWS CLI
aws s3 cp s3://seu-bucket/data/ data/ --recursive

# Exemplo com gsutil (Google Cloud)
gsutil -m cp -r gs://seu-bucket/data/* data/

# Exemplo com Azure CLI
az storage blob download-batch --destination data/ --source data-container
```

### 4. 🐳 Volumes Docker Externos

**Docker Compose com volume externo:**

```yaml
# docker-compose.yml
services:
  app:
    volumes:
      - external-data:/app/data

volumes:
  external-data:
    external: true
```

### 5. 📦 Dados Embedados na Imagem

**Para dados que não mudam frequentemente:**

```dockerfile
# No Dockerfile
COPY data/ /app/data/
```

## 🚀 Estratégia Recomendada para Produção

### Opção A: Git LFS (Atual)
```bash
git clone https://github.com/mbressan/otimizador-entrevistas-decision.git
cd otimizador-entrevistas-decision
./scripts/deploy.sh
```

### Opção B: CI/CD com Storage Externo
```yaml
# .github/workflows/deploy.yml
- name: Download Training Data
  run: |
    aws s3 cp s3://ml-training-data/applicants.json data/
    aws s3 cp s3://ml-training-data/vagas.json data/
    aws s3 cp s3://ml-training-data/prospects.json data/
```

## 🔄 Backup e Sincronização

### Script de Backup
```bash
#!/bin/bash
# scripts/backup-data.sh

# Backup para múltiplos destinos
aws s3 cp data/ s3://backup-bucket/data/ --recursive
rsync -av data/ backup-server:/backup/ml-data/
```

### Sincronização Automática
```bash
# Cron job para sincronização
0 2 * * * /path/to/scripts/backup-data.sh
```

## ⚡ Performance e Otimização

### Compressão de Dados
```bash
# Comprimir dados para reduzir tamanho
gzip data/*.json
```

### Dados Sintéticos para Desenvolvimento
```python
# scripts/generate-sample-data.py
import json
import random

# Gerar subset dos dados para desenvolvimento
with open('data/applicants.json') as f:
    data = json.load(f)
    
sample = random.sample(data, 1000)  # 1000 amostras
with open('data/applicants-sample.json', 'w') as f:
    json.dump(sample, f)
```

## 🔒 Segurança e Compliance

### Dados Sensíveis
- ✅ Nunca commitar dados pessoais reais
- ✅ Usar dados anonimizados/sintéticos
- ✅ Configurar .gitignore adequadamente
- ✅ Criptografar dados em repouso

### Controle de Acesso
```bash
# Restringir acesso aos dados
chmod 600 data/*.json
chown app:app data/*.json
```

## 📋 Checklist de Deploy

- [ ] ✅ Git LFS configurado
- [ ] ✅ Arquivos de dados disponíveis
- [ ] ✅ Script de deploy testado
- [ ] ✅ Backup dos dados configurado
- [ ] ✅ Monitoramento implementado
- [ ] ✅ Logs de erro configurados
- [ ] ✅ Health checks funcionando

## 🛠️ Troubleshooting

### Problema: Git LFS não baixa arquivos
```bash
# Solução
git lfs install
git lfs pull
```

### Problema: Arquivos muito grandes
```bash
# Solução: Usar streaming ou chunking
# Implementar download progressivo
```

### Problema: Falha na inicialização do banco
```bash
# Verificar logs
docker-compose logs postgresql
docker-compose logs app

# Verificar dados
ls -la data/
```

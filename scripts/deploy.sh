#!/bin/bash

# 🚀 Script de Deploy Automatizado - Otimizador de Entrevistas
# Este script facilita o deploy em diferentes ambientes

set -e  # Para o script se houver erro

echo "🚀 Iniciando deploy do Otimizador de Entrevistas..."

# Verificar se Git LFS está disponível
if ! command -v git-lfs &> /dev/null; then
    echo "⚠️ Git LFS não encontrado. Instalando..."
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
    sudo apt-get install git-lfs
    git lfs install
fi

# Verificar se Docker está disponível
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Instale Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Instale Docker Compose primeiro."
    exit 1
fi

# Baixar arquivos LFS
echo "📥 Baixando arquivos de dados via Git LFS..."
git lfs pull

# Verificar se os arquivos de dados existem
if [ ! -f "data/applicants.json" ] || [ ! -f "data/vagas.json" ] || [ ! -f "data/prospects.json" ]; then
    echo "❌ Arquivos de dados não encontrados!"
    echo "💡 Certifique-se de que os arquivos estão disponíveis via:"
    echo "   1. Git LFS (recomendado)"
    echo "   2. Download manual"
    echo "   3. Backup/Storage externo"
    exit 1
fi

# Verificar tamanho dos arquivos
echo "📊 Verificando arquivos de dados:"
ls -lh data/

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e executar
echo "🔨 Construindo e iniciando containers..."
docker-compose up --build -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
docker-compose ps

# Verificar logs da aplicação
echo "📝 Verificando logs da aplicação (últimas 20 linhas):"
docker-compose logs --tail=20 app

# Testar endpoints
echo "🧪 Testando endpoints básicos..."
curl -f http://localhost/health || echo "⚠️ Health check falhou"

echo "✅ Deploy concluído!"
echo ""
echo "🌐 Acesse os serviços:"
echo "   📱 Aplicação: http://localhost"
echo "   📊 Prometheus: http://localhost:9090"
echo "   📈 Grafana: http://localhost:3000 (admin/admin123)"
echo ""
echo "📋 Comandos úteis:"
echo "   docker-compose logs -f app       # Ver logs em tempo real"
echo "   docker-compose exec app bash     # Acessar container"
echo "   docker-compose down              # Parar serviços"

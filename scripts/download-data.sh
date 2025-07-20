#!/bin/bash

# 📥 Script de Download de Dados - Alternativa ao Git LFS
# Use este script se Git LFS não estiver disponível

set -e

echo "📥 Iniciando download dos dados de treinamento..."

# Criar diretório de dados se não existir
mkdir -p data

# URLs de exemplo - substitua pelos URLs reais dos seus dados
DATA_BASE_URL="https://github.com/mbressan/otimizador-entrevistas-decision/releases/download/v1.0.0"

# Função para download com retry
download_with_retry() {
    local url=$1
    local output=$2
    local max_attempts=3
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo "📡 Tentativa $attempt/$max_attempts - Baixando $output..."
        
        if curl -L -f -o "$output" "$url"; then
            echo "✅ $output baixado com sucesso"
            return 0
        else
            echo "❌ Falha na tentativa $attempt"
            attempt=$((attempt + 1))
            sleep 2
        fi
    done
    
    echo "❌ Falha ao baixar $output após $max_attempts tentativas"
    return 1
}

# Verificar se curl está disponível
if ! command -v curl &> /dev/null; then
    echo "❌ curl não encontrado. Instalando..."
    sudo apt-get update && sudo apt-get install -y curl
fi

# Download dos arquivos
echo "📊 Baixando arquivos de dados..."

# Opção 1: GitHub Releases (recomendado para arquivos grandes)
# download_with_retry "$DATA_BASE_URL/applicants.json" "data/applicants.json"
# download_with_retry "$DATA_BASE_URL/vagas.json" "data/vagas.json"
# download_with_retry "$DATA_BASE_URL/prospects.json" "data/prospects.json"

# Opção 2: Usar Git LFS como fallback
if command -v git-lfs &> /dev/null; then
    echo "🔧 Git LFS disponível, usando como fallback..."
    git lfs pull
elif [ -f ".gitattributes" ] && grep -q "*.json filter=lfs" .gitattributes; then
    echo "⚠️ Arquivos LFS detectados mas Git LFS não disponível"
    echo "💡 Instale Git LFS ou configure download alternativo"
    exit 1
fi

# Opção 3: Gerar dados sintéticos para desenvolvimento
generate_sample_data() {
    echo "🔬 Gerando dados sintéticos para desenvolvimento..."
    
    # Gerar dados mínimos para teste
    cat > data/applicants.json << 'EOF'
[
  {
    "id": 1,
    "nome": "João Silva",
    "competencias": "python flask postgresql",
    "nivel_profissional": "senior",
    "areas_atuacao": "desenvolvimento"
  },
  {
    "id": 2,
    "nome": "Maria Santos",
    "competencias": "javascript react nodejs",
    "nivel_profissional": "pleno",
    "areas_atuacao": "frontend"
  }
]
EOF

    cat > data/vagas.json << 'EOF'
[
  {
    "id": 1,
    "titulo": "Desenvolvedor Python Senior",
    "competencias_tecnicas": "python flask postgresql docker",
    "nivel": "senior",
    "area": "desenvolvimento"
  }
]
EOF

    cat > data/prospects.json << 'EOF'
[
  {
    "candidato_id": 1,
    "vaga_id": 1,
    "situacao": "contratado"
  },
  {
    "candidato_id": 2,
    "vaga_id": 1,
    "situacao": "rejeitado"
  }
]
EOF

    echo "✅ Dados sintéticos gerados"
}

# Verificar se os arquivos existem
if [ ! -f "data/applicants.json" ] || [ ! -f "data/vagas.json" ] || [ ! -f "data/prospects.json" ]; then
    echo "⚠️ Arquivos de dados não encontrados"
    echo "🔬 Gerando dados sintéticos para desenvolvimento..."
    generate_sample_data
fi

# Verificar integridade dos dados
echo "🔍 Verificando integridade dos dados..."
for file in data/*.json; do
    if [ -f "$file" ]; then
        echo "📄 $file: $(wc -l < "$file") linhas, $(du -h "$file" | cut -f1)"
        
        # Verificar se é JSON válido
        if python3 -m json.tool "$file" > /dev/null 2>&1; then
            echo "✅ $file é um JSON válido"
        else
            echo "❌ $file tem formato JSON inválido"
            exit 1
        fi
    fi
done

echo ""
echo "✅ Download/verificação dos dados concluída!"
echo ""
echo "📋 Próximos passos:"
echo "   1. Execute: docker-compose up --build"
echo "   2. Ou use: ./scripts/deploy.sh"
echo ""
echo "💡 Dicas:"
echo "   - Para dados reais, configure URLs no início deste script"
echo "   - Para produção, use Git LFS ou armazenamento em nuvem"
echo "   - Consulte DATA_MANAGEMENT.md para mais opções"

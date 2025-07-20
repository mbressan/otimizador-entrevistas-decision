#!/bin/bash

# Script para retreinamento automático do modelo de candidatos contratados
# Para ser executado via cron

# Configurações
API_URL="http://localhost:5000"
LOG_FILE="/var/log/model_retrain.log"
WEBHOOK_URL=""  # Opcional: webhook para notificações

# Função de log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Função para enviar notificação
notify() {
    local message="$1"
    local status="$2"
    
    log "$message"
    
    if [[ -n "$WEBHOOK_URL" ]]; then
        curl -X POST "$WEBHOOK_URL" \
             -H "Content-Type: application/json" \
             -d "{\"text\":\"🤖 **Modelo ML**: $message\", \"status\":\"$status\"}" \
             > /dev/null 2>&1
    fi
}

# Verificar saúde do modelo
log "Verificando saúde do modelo..."

health_response=$(curl -s "$API_URL/api/model_health")
health_status=$?

if [[ $health_status -ne 0 ]]; then
    notify "❌ Erro ao verificar saúde do modelo" "error"
    exit 1
fi

# Extrair informações da resposta
needs_retrain=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['needs_retrain'])")
priority=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['priority'])")
age_days=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['age_days'])")
new_data_count=$(echo "$health_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['new_data_count'])")

log "Status do modelo: needs_retrain=$needs_retrain, priority=$priority, age_days=$age_days, new_data=$new_data_count"

# Decidir se deve retreinar
should_retrain=false

if [[ "$needs_retrain" == "True" ]] && [[ "$priority" == "high" ]]; then
    should_retrain=true
    log "Retreinamento necessário - prioridade alta"
elif [[ "$age_days" -gt 90 ]]; then
    should_retrain=true
    log "Retreinamento necessário - modelo muito antigo ($age_days dias)"
elif [[ "$new_data_count" -gt 1000 ]]; then
    should_retrain=true
    log "Retreinamento necessário - muitos dados novos ($new_data_count)"
fi

if [[ "$should_retrain" == "true" ]]; then
    notify "🔄 Iniciando retreinamento automático do modelo" "info"
    
    # Executar retreinamento
    retrain_response=$(curl -s -X POST "$API_URL/api/retrain_model" \
                            -H "Content-Type: application/json" \
                            -d '{"force":false}')
    retrain_status=$?
    
    if [[ $retrain_status -eq 0 ]]; then
        status=$(echo "$retrain_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
        
        if [[ "$status" == "success" ]]; then
            # Extrair nova acurácia
            new_accuracy=$(echo "$retrain_response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{data['new_metadata']['accuracy']:.1%}\")" 2>/dev/null)
            notify "✅ Retreinamento concluído com sucesso! Nova acurácia: $new_accuracy" "success"
        else
            notify "⚠️ Retreinamento finalizado com status: $status" "warning"
        fi
    else
        notify "❌ Erro durante o retreinamento" "error"
    fi
else
    log "Retreinamento não necessário no momento"
fi

# Verificar se o modelo está carregado
model_info=$(curl -s "$API_URL/model/info")
model_loaded=$(echo "$model_info" | python3 -c "import sys, json; print(json.load(sys.stdin)['model_loaded'])" 2>/dev/null)

if [[ "$model_loaded" != "True" ]]; then
    notify "❌ Modelo não está carregado!" "error"
fi

log "Verificação concluída"

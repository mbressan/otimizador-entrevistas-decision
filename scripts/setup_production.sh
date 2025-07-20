#!/bin/bash

# Script de configuração para ambiente de produção
# Configura monitoramento, logs e serviços

set -e

echo "🚀 Configurando ambiente de produção..."

# Criar diretórios necessários
sudo mkdir -p /var/log/ml-optimizer
sudo mkdir -p /etc/ml-optimizer

# Configurar permissões de log
sudo chown $USER:$USER /var/log/ml-optimizer
sudo chmod 755 /var/log/ml-optimizer

# Criar arquivo de configuração principal
cat > /etc/ml-optimizer/config.json << EOF
{
    "model": {
        "retrain_interval_days": 30,
        "min_accuracy_threshold": 0.85,
        "max_model_age_days": 90,
        "min_new_data_for_retrain": 500
    },
    "monitoring": {
        "prometheus_enabled": true,
        "metrics_port": 9090,
        "log_level": "INFO"
    },
    "api": {
        "rate_limit": "100/hour",
        "cors_enabled": true,
        "auth_required": false
    },
    "notifications": {
        "webhook_url": "",
        "email_alerts": false,
        "slack_integration": false
    }
}
EOF

# Criar serviço systemd para a aplicação
cat > /etc/systemd/system/ml-optimizer.service << EOF
[Unit]
Description=ML Optimizer API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/mateus/otimizador-entrevistas-decision
Environment=PATH=/usr/bin:/usr/local/bin
Environment=PYTHONPATH=/home/mateus/otimizador-entrevistas-decision
ExecStart=/usr/bin/python3 app/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ml-optimizer

[Install]
WantedBy=multi-user.target
EOF

# Configurar logrotate
cat > /etc/logrotate.d/ml-optimizer << EOF
/var/log/ml-optimizer/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload ml-optimizer
    endscript
}
EOF

# Instalar dependências de sistema
echo "📦 Instalando dependências..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    postgresql-client \
    curl \
    jq \
    logrotate \
    cron

# Configurar ambiente Python
echo "🐍 Configurando ambiente Python..."
cd /home/mateus/otimizador-entrevistas-decision
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt

# Adicionar dependências de produção
pip install gunicorn supervisor

# Configurar Gunicorn
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
preload_app = True
access_logfile = "/var/log/ml-optimizer/access.log"
error_logfile = "/var/log/ml-optimizer/error.log"
capture_output = True
enable_stdio_inheritance = True
EOF

# Criar script de inicialização
cat > start_production.sh << EOF
#!/bin/bash
cd /home/mateus/otimizador-entrevistas-decision
source venv/bin/activate
exec gunicorn --config gunicorn.conf.py app.app:app
EOF

chmod +x start_production.sh

# Atualizar o serviço systemd
sed -i 's|ExecStart=.*|ExecStart=/home/mateus/otimizador-entrevistas-decision/start_production.sh|' /etc/systemd/system/ml-optimizer.service

# Configurar Prometheus (se não estiver rodando)
if ! command -v prometheus &> /dev/null; then
    echo "📊 Configurando Prometheus..."
    
    # Download Prometheus
    cd /tmp
    wget https://github.com/prometheus/prometheus/releases/download/v2.40.0/prometheus-2.40.0.linux-amd64.tar.gz
    tar xfz prometheus-*.tar.gz
    sudo mv prometheus-*/prometheus /usr/local/bin/
    sudo mv prometheus-*/promtool /usr/local/bin/
    
    # Criar usuário prometheus
    sudo useradd --no-create-home --shell /bin/false prometheus
    
    # Criar diretórios
    sudo mkdir -p /etc/prometheus /var/lib/prometheus
    sudo chown prometheus:prometheus /etc/prometheus /var/lib/prometheus
    
    # Configurar Prometheus
    sudo cp prometheus.yml /etc/prometheus/
    sudo chown prometheus:prometheus /etc/prometheus/prometheus.yml
    
    # Criar serviço
    cat > /etc/systemd/system/prometheus.service << PROM_EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \\
    --config.file /etc/prometheus/prometheus.yml \\
    --storage.tsdb.path /var/lib/prometheus/ \\
    --web.console.templates=/etc/prometheus/consoles \\
    --web.console.libraries=/etc/prometheus/console_libraries \\
    --web.listen-address=0.0.0.0:9090

[Install]
WantedBy=multi-user.target
PROM_EOF
fi

# Habilitar serviços
echo "⚙️ Habilitando serviços..."
sudo systemctl daemon-reload
sudo systemctl enable ml-optimizer
sudo systemctl enable prometheus

# Configurar firewall (opcional)
if command -v ufw &> /dev/null; then
    echo "🔥 Configurando firewall..."
    sudo ufw allow 5000/tcp  # API
    sudo ufw allow 9090/tcp  # Prometheus
    sudo ufw allow 3000/tcp  # Grafana
fi

# Configurar cron para retreinamento
echo "⏰ Configurando retreinamento automático..."
(crontab -l 2>/dev/null; echo "0 2 * * * /home/mateus/otimizador-entrevistas-decision/scripts/auto_retrain.sh") | crontab -

echo "✅ Configuração de produção concluída!"
echo ""
echo "Para iniciar os serviços:"
echo "  sudo systemctl start ml-optimizer"
echo "  sudo systemctl start prometheus"
echo ""
echo "Para verificar status:"
echo "  sudo systemctl status ml-optimizer"
echo "  journalctl -u ml-optimizer -f"
echo ""
echo "URLs importantes:"
echo "  API: http://localhost:5000"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000"
echo ""
echo "Logs:"
echo "  tail -f /var/log/ml-optimizer/error.log"
echo "  tail -f /var/log/model_retrain.log"

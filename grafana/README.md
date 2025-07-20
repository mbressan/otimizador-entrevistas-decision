# Configuração do Grafana
# Este arquivo será usado como referência para configurações adicionais

# Dashboards incluídos:
# 1. main-dashboard.json - Dashboard principal com métricas da aplicação e ML
# 2. infrastructure-dashboard.json - Dashboard de infraestrutura e containers

# Para adicionar novos dashboards:
# 1. Crie o arquivo JSON na pasta grafana/dashboards/
# 2. Reinicie o container do Grafana: docker-compose restart grafana

# Configurações principais:
# - Admin password: admin123
# - Datasource: Prometheus (http://prometheus:9090)
# - Auto-provisioning habilitado
# - Dashboard padrão: main-dashboard.json

# URLs de acesso:
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
# - Application: http://localhost (via Nginx)

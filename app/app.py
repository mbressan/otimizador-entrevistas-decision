import os
import json
import pandas as pd
import joblib
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Histogram, Gauge

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Configurar métricas Prometheus
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='2.0.0')

# Métricas específicas para o modelo de candidatos contratados
hired_model_predictions = Counter(
    'hired_model_predictions_total',
    'Total de predições do modelo de candidatos contratados',
    ['prediction_type', 'quality_level']
)

quality_scores = Histogram(
    'hired_model_quality_scores',
    'Distribuição dos scores de qualidade do modelo',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

model_accuracy = Gauge('hired_model_accuracy', 'Acurácia do modelo de candidatos contratados')
model_samples = Gauge('hired_model_training_samples', 'Número de amostras usadas no treinamento')

# Caminhos dos arquivos
BASE_DIR = Path(__file__).parent

# Variáveis globais para modelo
pipeline_model = None

def prepare_hired_candidates_features(vaga_row, candidate_row):
    """Prepara features baseadas em padrões de candidatos contratados"""
    
    def calculate_tech_success_score(competencias_vaga, conhecimentos_cand):
        """Calcula compatibilidade técnica baseada em padrões de contratação"""
        comp_vaga = str(competencias_vaga).lower() if competencias_vaga else ''
        conhec_cand = str(conhecimentos_cand).lower() if conhecimentos_cand else ''
        
        if not comp_vaga or not conhec_cand:
            return 0.5
        
        # Tecnologias mais valorizadas em contratações
        high_value_techs = ['python', 'java', 'javascript', 'react', 'angular', 'sql', 
                           'aws', 'docker', 'kubernetes', 'spring', 'django', 'flask']
        
        comp_words = set(comp_vaga.split())
        conhec_words = set(conhec_cand.split())
        
        # Score básico de match
        if len(comp_words) == 0:
            return 0.5
        
        basic_match = len(comp_words.intersection(conhec_words)) / len(comp_words)
        
        # Bonus para tecnologias de alto valor
        high_value_matches = sum(1 for tech in high_value_techs 
                               if tech in comp_vaga and tech in conhec_cand)
        tech_bonus = min(0.3, high_value_matches * 0.1)
        
        return min(1.0, basic_match + tech_bonus)
    
    def calculate_academic_success_score(nivel_vaga, nivel_cand):
        """Calcula score acadêmico baseado em padrões de contratação"""
        nivel_vaga = str(nivel_vaga).lower() if nivel_vaga else ''
        nivel_cand = str(nivel_cand).lower() if nivel_cand else ''
        
        hierarchy = {
            'fundamental': 1, 'médio': 2, 'técnico': 3,
            'superior': 4, 'pós': 5, 'mestrado': 6, 'doutorado': 7
        }
        
        vaga_level = max([v for k, v in hierarchy.items() if k in nivel_vaga] or [3])
        cand_level = max([v for k, v in hierarchy.items() if k in nivel_cand] or [3])
        
        if cand_level >= vaga_level:
            return 1.0
        elif cand_level >= vaga_level - 1:
            return 0.8
        else:
            return 0.5
    
    def calculate_english_success_score(nivel_vaga, nivel_cand):
        """Calcula score de inglês baseado em padrões de contratação"""
        nivel_vaga = str(nivel_vaga).lower() if nivel_vaga else ''
        nivel_cand = str(nivel_cand).lower() if nivel_cand else ''
        
        english_levels = {
            'básico': 1, 'intermediário': 2, 'avançado': 3, 'fluente': 4
        }
        
        vaga_level = max([v for k, v in english_levels.items() if k in nivel_vaga] or [1])
        cand_level = max([v for k, v in english_levels.items() if k in nivel_cand] or [1])
        
        return min(1.0, cand_level / max(vaga_level, 1))
    
    # Extrair dados das rows
    competencias_tecnicas = vaga_row.get('competencias_tecnicas_requeridas', '')
    conhecimentos_tecnicos = candidate_row.get('conhecimentos_tecnicos', '')
    nivel_academico_vaga = vaga_row.get('nivel_academico', '')
    nivel_academico_candidato = candidate_row.get('nivel_academico', '')
    nivel_ingles_vaga = vaga_row.get('nivel_ingles', '')
    nivel_ingles_candidato = candidate_row.get('nivel_ingles', '')
    areas_atuacao = vaga_row.get('areas_atuacao', '')
    area_atuacao_candidato = candidate_row.get('area_de_atuacao', '')
    tipo_contratacao = vaga_row.get('tipo_contratacao', '')
    titulo_vaga = vaga_row.get('titulo_vaga', '')
    nivel_profissional = vaga_row.get('nivel_profissional', '')
    
    # Criar features baseadas em padrões de sucesso
    features = {
        'tech_success_score': calculate_tech_success_score(competencias_tecnicas, conhecimentos_tecnicos),
        'academic_success_score': calculate_academic_success_score(nivel_academico_vaga, nivel_academico_candidato),
        'english_success_score': calculate_english_success_score(nivel_ingles_vaga, nivel_ingles_candidato),
        'is_clt': 1 if 'clt' in str(tipo_contratacao).lower() else 0,
        'is_pj': 1 if 'pj' in str(tipo_contratacao).lower() else 0,
        'is_tech_area': 1 if any(tech in str(areas_atuacao).lower() or tech in str(area_atuacao_candidato).lower() 
                                for tech in ['ti', 'tecnologia', 'desenvolvimento']) else 0,
        'nivel_profissional': str(nivel_profissional) if nivel_profissional else 'não_informado',
        'areas_atuacao': str(areas_atuacao) if areas_atuacao else 'não_informado',
        'area_atuacao_candidato': str(area_atuacao_candidato) if area_atuacao_candidato else 'não_informado',
        'combined_text': (
            str(titulo_vaga) + ' ' +
            str(competencias_tecnicas) + ' ' +
            str(conhecimentos_tecnicos) + ' ' +
            str(areas_atuacao)
        ).lower().strip()
    }
    
    # Tratar valores vazios
    for key, value in features.items():
        if value == '' or value == 'nan' or str(value) == 'nan':
            if key in ['tech_success_score', 'academic_success_score', 'english_success_score']:
                features[key] = 0.5
            elif key in ['is_clt', 'is_pj', 'is_tech_area']:
                features[key] = 0
            else:
                features[key] = 'não_informado'
    
    return pd.DataFrame([features])

def load_resources():
    """Carrega modelo ML na inicialização"""
    global pipeline_model
    
    print("🚀 Carregando recursos...")
    
    # Carregar modelo ML de candidatos contratados
    try:
        model_path = os.path.join(BASE_DIR, 'models', 'pipeline_candidatos_contratados.joblib')
        pipeline_model = joblib.load(model_path)
        
        # Carregar metadata do modelo
        metadata_path = os.path.join(BASE_DIR, 'models', 'metadata_candidatos_contratados.json')
        with open(metadata_path, 'r', encoding='utf-8') as f:
            model_metadata = json.load(f)
        
        print("✅ Modelo de candidatos contratados carregado!")
        print(f"   Tipo: {model_metadata.get('model_type', 'N/A')}")
        print(f"   Acurácia: {model_metadata.get('accuracy', 0):.1%}")
        print(f"   Data de treino: {model_metadata.get('trained_date', 'N/A')}")
        
        # Atualizar métricas do modelo
        model_accuracy.set(model_metadata.get('accuracy', 0))
        model_samples.set(model_metadata.get('n_samples', 0))
        
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        pipeline_model = None

# Rotas da aplicação
@app.route('/')
def index():
    """Página inicial com formulário de predição"""
    return render_template('index.html')

@app.route('/status')
def status_page():
    """Página de status do sistema"""
    return render_template('status.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'model_type': 'hired_candidates',
        'model_loaded': pipeline_model is not None
    }
    return jsonify(status)

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint para predições via API usando modelo de candidatos contratados"""
    try:
        if pipeline_model is None:
            return jsonify({'error': 'Modelo não carregado'}), 500
        
        data = request.get_json()
        
        # Verificar se os dados estão no formato vaga/candidato ou se são features diretas
        if 'vaga' in data and 'candidato' in data:
            # Formato vaga/candidato - usar prepare_hired_candidates_features
            vaga_data = data.get('vaga', {})
            candidato_data = data.get('candidato', {})
            
            if not vaga_data or not candidato_data:
                return jsonify({'error': 'Dados da vaga e candidato são obrigatórios'}), 400
            
            # Preparar features automaticamente
            features_data = prepare_hired_candidates_features(vaga_data, candidato_data)
            
            # Fazer predição
            prediction = pipeline_model.predict(features_data)[0]
            probability = pipeline_model.predict_proba(features_data)[0]
            
            # Extrair features calculadas
            features = features_data.iloc[0].to_dict()
            
            # Métricas de monitoramento
            quality_level = 'high' if prediction == 1 else 'low'
            hired_model_predictions.labels(
                prediction_type='unified_interface',
                quality_level=quality_level
            ).inc()
            
            quality_score = float(probability[1]) if len(probability) > 1 else 0.5
            quality_scores.observe(quality_score)
            
            # Resposta detalhada para interface web
            result = {
                'prediction': int(prediction),
                'prediction_text': 'ALTA QUALIDADE' if prediction == 1 else 'BAIXA QUALIDADE',
                'probability': {
                    'low_quality': float(probability[0]),
                    'high_quality': float(probability[1]) if len(probability) > 1 else 0.0
                },
                'quality_score': float(probability[1] * 100) if len(probability) > 1 else 50.0,
                'percentage': f"{probability[1] * 100:.1f}%" if len(probability) > 1 else "50.0%",
                'model_type': 'hired_candidates_unified',
                'match_score': float(probability[1] * 100) if len(probability) > 1 else 50.0,
                'explanation': {
                    'tech_compatibility': f"{features['tech_success_score']*100:.1f}%",
                    'academic_compatibility': f"{features['academic_success_score']*100:.1f}%",
                    'english_compatibility': f"{features['english_success_score']*100:.1f}%"
                },
                'analysis': {
                    'tech_compatibility': f"{features['tech_success_score']*100:.1f}%",
                    'academic_compatibility': f"{features['academic_success_score']*100:.1f}%", 
                    'english_compatibility': f"{features['english_success_score']*100:.1f}%",
                    'area_match': 'Área de TI' if features['is_tech_area'] else 'Outra área',
                    'contract_type': 'CLT' if features['is_clt'] else ('PJ' if features['is_pj'] else 'Outros')
                }
            }
            
        else:
            # Formato de features diretas (compatibilidade com versão anterior)
            required_fields = ['tech_match_score', 'nivel_profissional', 'areas_atuacao', 
                             'area_de_atuacao', 'academic_match', 'english_match', 'combined_text']
            
            # Verificar se tem os campos necessários
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return jsonify({'error': f'Campos obrigatórios: {missing_fields}'}), 400
            
            # Preparar dados para predição
            features_data = pd.DataFrame([data])
            
            # Fazer predição
            prediction = pipeline_model.predict(features_data)[0]
            probability = pipeline_model.predict_proba(features_data)[0]
            
            # Métricas de monitoramento
            quality_level = 'high' if prediction == 1 else 'low'
            hired_model_predictions.labels(
                prediction_type='api_direct',
                quality_level=quality_level
            ).inc()
            
            quality_score = float(probability[1]) if len(probability) > 1 else 0.5
            quality_scores.observe(quality_score)
            
            # Extrair features se usou prepare_hired_candidates_features
            tech_score = data.get('tech_match_score', 0.5)
            academic_score = 0.5  # Não disponível no formato antigo
            english_score = 0.5   # Não disponível no formato antigo
            
            result = {
                'prediction': int(prediction),
                'prediction_text': 'CONTRATADO' if prediction == 1 else 'NÃO CONTRATADO',
                'probability': {
                    'not_hired': float(probability[0]),
                    'hired': float(probability[1]) if len(probability) > 1 else 0.0
                },
                'match_score': float(probability[1] * 100) if len(probability) > 1 else 50.0,
                'model_type': 'hired_candidates',
                'explanation': {
                    'tech_compatibility': f"{tech_score*100:.1f}%",
                    'academic_compatibility': f"{academic_score*100:.1f}%",
                    'english_compatibility': f"{english_score*100:.1f}%"
                }
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Carregar recursos na inicialização do módulo
load_resources()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

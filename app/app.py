import os
import json
import pandas as pd
import joblib
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics

# Importar integração PostgreSQL
try:
    from postgresql_integration import (
        create_pg_engine,
        is_postgres_available,
        load_vagas_from_postgres,
        load_candidatos_from_postgres, 
        load_prospects_from_postgres,
        save_predicao_to_postgres,
        search_vagas_postgres,
        get_vagas_stats_postgres,
        get_candidatos_stats_postgres,
        get_prospects_stats_postgres,
        get_predicoes_stats_postgres,
        get_estados_postgres,
        get_cidades_postgres,
        get_clientes_postgres,
        get_niveis_profissionais_postgres,
        setup_postgres_database
    )
    from sqlalchemy import text
    POSTGRES_AVAILABLE = True
    print("✅ Integração PostgreSQL carregada")
except ImportError as e:
    print(f"⚠️  PostgreSQL não disponível: {e}")
    print("   Usando modo compatibilidade com arquivos JSON")
    POSTGRES_AVAILABLE = False
    
    # Definir funções de fallback
    def is_postgres_available():
        return False
    
    def create_pg_engine():
        return None
    
    def load_vagas_from_postgres():
        return pd.DataFrame()
    
    def load_candidatos_from_postgres():
        return pd.DataFrame()
    
    def load_prospects_from_postgres():
        return pd.DataFrame()
    
    def search_vagas_postgres(*args, **kwargs):
        return {'vagas': [], 'total': 0, 'total_pages': 0, 'niveis_unicos': []}

# Configuração da aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Configurar métricas Prometheus
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='2.0.0')

# Caminhos dos arquivos
BASE_DIR = Path(__file__).parent

# Variáveis globais para dados
pipeline_model = None
df_vagas = None
df_candidates = None
df_prospects = None
vagas_com_prospects = set()  # Cache das vagas que possuem prospects

def load_json_data(file_path):
    """Carrega dados JSON de um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo {file_path}: {e}")
        return {}

def normalize_vagas(vagas_data):
    """Normaliza dados das vagas"""
    vagas_list = []
    for vaga_id, vaga_info in vagas_data.items():
        try:
            # Extrair informações básicas
            info_basicas = vaga_info.get('informacoes_basicas', {})
            perfil_vaga = vaga_info.get('perfil_vaga', {})
            
            vaga_record = {
                'id_vaga': vaga_id,
                'data_requisicao': info_basicas.get('data_requicisao', ''),
                'titulo_vaga': info_basicas.get('titulo_vaga', ''),
                'cliente': info_basicas.get('cliente', ''),
                'tipo_contratacao': info_basicas.get('tipo_contratacao', ''),
                'pais': perfil_vaga.get('pais', ''),
                'estado': perfil_vaga.get('estado', ''),
                'cidade': perfil_vaga.get('cidade', ''),
                'nivel_profissional': perfil_vaga.get('nivel profissional', ''),
                'nivel_academico': perfil_vaga.get('nivel_academico', ''),
                'nivel_ingles': perfil_vaga.get('nivel_ingles', ''),
                'areas_atuacao': perfil_vaga.get('areas_atuacao', ''),
                'competencias_tecnicas_requeridas': perfil_vaga.get('competencia_tecnicas_e_comportamentais', ''),
                'principais_atividades': perfil_vaga.get('principais_atividades', '')
            }
            vagas_list.append(vaga_record)
        except Exception as e:
            print(f"Erro ao processar vaga {vaga_id}: {e}")
            continue
    
    return pd.DataFrame(vagas_list)

def normalize_applicants(applicants_data):
    """Normaliza dados dos candidatos"""
    applicants_list = []
    for candidato_id, candidato_info in applicants_data.items():
        try:
            # Extrair informações
            info_basicas = candidato_info.get('infos_basicas', {})
            info_pessoais = candidato_info.get('informacoes_pessoais', {})
            info_profissionais = candidato_info.get('informacoes_profissionais', {})
            formacao = candidato_info.get('formacao', {})
            
            candidato_record = {
                'codigo_candidato': candidato_id,
                'nome': info_basicas.get('nome', ''),
                'email': info_basicas.get('email', ''),
                'telefone': info_basicas.get('telefone', ''),
                'data_nascimento': info_pessoais.get('data_nascimento', ''),
                'estado_civil': info_pessoais.get('estado_civil', ''),
                'pcd': info_pessoais.get('pcd', ''),
                'nivel_academico': formacao.get('nivel_academico', ''),
                'area_formacao': formacao.get('area_formacao', ''),
                'nivel_ingles': info_profissionais.get('nivel_ingles', ''),
                'conhecimentos_tecnicos': info_profissionais.get('conhecimentos_tecnicos', ''),
                'area_de_atuacao': info_profissionais.get('area_de_atuacao', '')
            }
            applicants_list.append(candidato_record)
        except Exception as e:
            print(f"Erro ao processar candidato {candidato_id}: {e}")
            continue
    
    return pd.DataFrame(applicants_list)

def prepare_enhanced_features(vaga_row, candidate_row):
    """Prepara features avançadas para o modelo aprimorado"""
    
    def calculate_tech_match(competencias_req, conhecimentos):
        """Calcula match entre competências requeridas e conhecimentos técnicos"""
        comp_req = str(competencias_req).lower() if competencias_req else ''
        conhec = str(conhecimentos).lower() if conhecimentos else ''
        
        if not comp_req or comp_req == 'nan' or not conhec or conhec == 'nan':
            return 0.0
            
        comp_words = set(comp_req.split())
        conhec_words = set(conhec.split())
        
        if len(comp_words) == 0:
            return 0.0
            
        intersection = comp_words.intersection(conhec_words)
        return len(intersection) / len(comp_words)
    
    def calculate_academic_match(nivel_vaga, nivel_candidato):
        """Calcula compatibilidade acadêmica"""
        hierarchy = {
            'ensino médio': 1, 'técnico': 2, 'tecnólogo': 3,
            'superior': 4, 'pós-graduação': 5, 'mestrado': 6, 'doutorado': 7
        }
        
        vaga_level = hierarchy.get(str(nivel_vaga).lower(), 0)
        candidato_level = hierarchy.get(str(nivel_candidato).lower(), 0)
        
        if vaga_level == 0 or candidato_level == 0:
            return 'indefinido'
        return 'compatível' if candidato_level >= vaga_level else 'insuficiente'
    
    def calculate_english_match(nivel_vaga, nivel_candidato):
        """Calcula compatibilidade de inglês"""
        hierarchy = {
            'nenhum': 0, 'básico': 1, 'intermediário': 2,
            'avançado': 3, 'fluente': 4, 'nativo': 5
        }
        
        vaga_level = hierarchy.get(str(nivel_vaga).lower(), -1)
        candidato_level = hierarchy.get(str(nivel_candidato).lower(), -1)
        
        if vaga_level == -1 or candidato_level == -1:
            return 'indefinido'
        return 'compatível' if candidato_level >= vaga_level else 'insuficiente'
    
    # Criar features avançadas
    features = {
        'tech_match_score': calculate_tech_match(
            vaga_row.get('competencias_tecnicas_requeridas'),
            candidate_row.get('conhecimentos_tecnicos')
        ),
        'nivel_profissional': str(vaga_row.get('nivel_profissional', '')).lower().strip(),
        'areas_atuacao': str(vaga_row.get('areas_atuacao', '')).lower().strip(),
        'area_de_atuacao': str(candidate_row.get('area_de_atuacao', '')).lower().strip(),
        'academic_match': calculate_academic_match(
            vaga_row.get('nivel_academico'),
            candidate_row.get('nivel_academico')
        ),
        'english_match': calculate_english_match(
            vaga_row.get('nivel_ingles'),
            candidate_row.get('nivel_ingles')
        ),
        'combined_text': ' '.join([
            str(vaga_row.get('competencias_tecnicas_requeridas', '')),
            str(candidate_row.get('conhecimentos_tecnicos', '')),
            str(vaga_row.get('principais_atividades', '')),
            str(candidate_row.get('area_de_atuacao', ''))
        ]).lower().strip()
    }
    
    # Tratar valores vazios
    for key, value in features.items():
        if value == '' or value == 'nan':
            features[key] = 'não_informado'
    
    return pd.DataFrame([features])

def initialize_database():
    """
    Inicializa o banco de dados PostgreSQL automaticamente durante o startup da aplicação.
    Cria esquema e popula com dados dos arquivos JSON se necessário.
    """
    print("🔍 Verificando estado do banco de dados PostgreSQL...")
    
    try:
        # Verificar se PostgreSQL está disponível
        if not POSTGRES_AVAILABLE or not is_postgres_available():
            print("⚠️ PostgreSQL não está disponível. Aplicação usará modo fallback JSON.")
            return False
        
        print("✅ PostgreSQL está disponível!")
        
        # Verificar se já existem dados no banco
        engine = create_pg_engine()
        if engine is None:
            print("❌ Não foi possível criar conexão com PostgreSQL.")
            return False
            
        with engine.connect() as conn:
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM vagas")).fetchone()
                vagas_count = result[0] if result else 0
                
                if vagas_count > 0:
                    print(f"ℹ️ Banco já contém {vagas_count} vagas. Pulando inicialização.")
                    return True
                else:
                    print("📝 Banco vazio detectado. Iniciando população automática...")
                    
            except Exception:
                # Tabela provavelmente não existe, precisamos criar esquema
                print("🏗️ Esquema do banco não encontrado. Criando estrutura...")
        
        # Configurar banco (criar esquema e migrar dados)
        if POSTGRES_AVAILABLE:
            setup_success = setup_postgres_database()
            
            if setup_success:
                print("🎉 Banco de dados inicializado com sucesso!")
                return True
            else:
                print("❌ Falha na inicialização do banco de dados.")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"❌ Erro durante inicialização do banco: {e}")
        print("   A aplicação continuará em modo fallback JSON.")
        return False

def load_resources():
    """Carrega modelo ML e dados na inicialização"""
    global pipeline_model, df_vagas, df_candidates, df_prospects, vagas_com_prospects
    
    print("🚀 Carregando recursos...")
    
    # ETAPA 1: Inicialização automática do banco de dados PostgreSQL
    print("\n=== INICIALIZAÇÃO DO BANCO DE DADOS ===")
    initialize_database()
    
    # ETAPA 2: Carregar modelo ML
    try:
        model_path = os.path.join(BASE_DIR, 'models', 'pipeline_aprimorado.joblib')
        pipeline_model = joblib.load(model_path)
        print("✅ Modelo ML aprimorado carregado!")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        pipeline_model = None
    
    # Inicializar variáveis globais
    df_vagas = pd.DataFrame()
    df_candidates = pd.DataFrame()
    df_prospects = pd.DataFrame()
    vagas_com_prospects = set()
    
    # Verificar se PostgreSQL está disponível
    if not is_postgres_available():
        print("⚠️ PostgreSQL não disponível - carregando dados JSON como fallback")
        
        # Fallback para dados JSON
        try:
            # Carregar vagas JSON
            vagas_path = os.path.join(BASE_DIR, 'data', 'vagas.json')
            if os.path.exists(vagas_path):
                with open(vagas_path, 'r', encoding='utf-8') as f:
                    vagas_data = json.load(f)
                df_vagas = pd.DataFrame.from_dict(vagas_data, orient='index')
                print(f"✅ {len(df_vagas)} vagas carregadas do JSON!")
            else:
                df_vagas = pd.DataFrame()
                print("✅ 0 vagas carregadas!")
            
            # Carregar candidatos JSON
            candidates_path = os.path.join(BASE_DIR, 'data', 'applicants.json')
            if os.path.exists(candidates_path):
                with open(candidates_path, 'r', encoding='utf-8') as f:
                    candidates_data = json.load(f)
                df_candidates = pd.DataFrame(candidates_data)
                print(f"✅ {len(df_candidates)} candidatos carregados do JSON!")
            else:
                df_candidates = pd.DataFrame()
                print("✅ 0 candidatos carregados!")
            
            # Carregar prospects JSON
            prospects_path = os.path.join(BASE_DIR, 'data', 'prospects.json')
            if os.path.exists(prospects_path):
                with open(prospects_path, 'r', encoding='utf-8') as f:
                    prospects_data = json.load(f)
                
                # Converter para DataFrame
                prospects_list = []
                for vaga_id, vaga_data in prospects_data.items():
                    for prospect in vaga_data.get('prospects', []):
                        prospect['id_vaga'] = vaga_id
                        prospects_list.append(prospect)
                
                df_prospects = pd.DataFrame(prospects_list)
                vagas_com_prospects = set(df_prospects['id_vaga'].unique()) if not df_prospects.empty else set()
                
                print(f"✅ {len(vagas_com_prospects)} vagas com prospects identificadas!")
                print(f"✅ Total de {len(df_prospects)} prospects carregados do JSON!")
            else:
                df_prospects = pd.DataFrame()
                vagas_com_prospects = set()
                print("✅ 0 prospects carregados!")
                
        except Exception as e:
            print(f"❌ Erro no fallback JSON: {e}")
            df_vagas = pd.DataFrame()
            df_candidates = pd.DataFrame()
            df_prospects = pd.DataFrame()
            vagas_com_prospects = set()
        
        return
    
    # Carregar dados das vagas do PostgreSQL
    try:
        vagas_dict = load_vagas_from_postgres()
        if vagas_dict:
            df_vagas = pd.DataFrame.from_dict(vagas_dict, orient='index')
            print(f"✅ {len(df_vagas)} vagas carregadas do PostgreSQL!")
        else:
            df_vagas = pd.DataFrame()
            print("✅ 0 vagas carregadas!")
    except Exception as e:
        print(f"❌ Erro ao carregar vagas do PostgreSQL: {e}")
        df_vagas = pd.DataFrame()
        print("✅ 0 vagas carregadas!")
    
    # Carregar dados dos candidatos do PostgreSQL
    try:
        candidates_list = load_candidatos_from_postgres()
        if candidates_list:
            df_candidates = pd.DataFrame(candidates_list)
            print(f"✅ {len(df_candidates)} candidatos carregados do PostgreSQL!")
        else:
            df_candidates = pd.DataFrame()
            print("✅ 0 candidatos carregados!")
    except Exception as e:
        print(f"❌ Erro ao carregar candidatos do PostgreSQL: {e}")
        df_candidates = pd.DataFrame()
        print("✅ 0 candidatos carregados!")
    
    # Carregar dados dos prospects do PostgreSQL e identificar vagas com prospects
    try:
        prospects_dict = load_prospects_from_postgres()
        if prospects_dict:
            # Converter para DataFrame
            prospects_list = []
            for vaga_id, vaga_data in prospects_dict.items():
                for prospect in vaga_data.get('prospects', []):
                    prospect['id_vaga'] = vaga_id
                    prospects_list.append(prospect)
            
            df_prospects = pd.DataFrame(prospects_list)
            vagas_com_prospects = set(df_prospects['id_vaga'].unique()) if not df_prospects.empty else set()
        else:
            df_prospects = pd.DataFrame()
            vagas_com_prospects = set()
        
        print(f"✅ {len(vagas_com_prospects)} vagas com prospects identificadas!")
        print(f"✅ Total de {len(df_prospects)} prospects carregados do PostgreSQL!")
    except Exception as e:
        print(f"❌ Erro ao carregar prospects do PostgreSQL: {e}")
        df_prospects = pd.DataFrame()
        vagas_com_prospects = set()
        print("✅ 0 prospects carregados!")

# Carregar recursos na inicialização do módulo
load_resources()

# Rotas da aplicação
@app.route('/')
def index():
    """Página inicial com lista de vagas paginada e com busca usando PostgreSQL"""
    try:
        # Parâmetros de paginação e busca
        page = request.args.get('page', 1, type=int)
        per_page = 10  # 10 vagas por página
        search = request.args.get('search', '', type=str)
        nivel_filter = request.args.get('nivel', '', type=str)
        
        # Verificar se PostgreSQL está disponível
        if not is_postgres_available():
            return render_template('index.html', 
                                 vagas=[], 
                                 pagination={'pages': 0, 'current_page': 1, 'total': 0},
                                 search=search,
                                 nivel_filter=nivel_filter,
                                 niveis_unicos=[],
                                 error="PostgreSQL não disponível")
        
        # Usar função de busca do PostgreSQL
        try:
            result = search_vagas_postgres(
                search_term=search if search else '',
                nivel_filter=nivel_filter if nivel_filter else '',
                page=page,
                per_page=per_page
            )
            
            # Extrair dados do resultado
            vagas_display = result['vagas']
            total_vagas = result['total']
            total_pages = result['total_pages']
            niveis_unicos = result.get('niveis_unicos', [])
            
        except Exception as e:
            print(f"❌ Erro na busca PostgreSQL: {e}")
            # Fallback para busca tradicional se houver erro
            if df_vagas is None or df_vagas.empty:
                return "Erro: Dados de vagas não carregados e PostgreSQL indisponível", 500
            
            # Filtrar apenas vagas que possuem prospects
            vagas_filtradas = df_vagas[df_vagas['id_vaga'].isin(vagas_com_prospects)].copy()
            
            if vagas_filtradas.empty:
                return render_template('index.html', 
                                     vagas=[], 
                                     pagination={'pages': 0, 'current_page': 1, 'total': 0},
                                     search=search,
                                     nivel_filter=nivel_filter,
                                     niveis_unicos=[])
            
            # Aplicar filtros de busca
            if search:
                search_lower = search.lower()
                mask = (
                    vagas_filtradas['titulo_vaga'].str.lower().str.contains(search_lower, na=False) |
                    vagas_filtradas['cliente'].str.lower().str.contains(search_lower, na=False) |
                    vagas_filtradas['areas_atuacao'].str.lower().str.contains(search_lower, na=False)
                )
                vagas_filtradas = vagas_filtradas[mask]
            
            # Aplicar filtro de nível
            if nivel_filter:
                nivel_filter_lower = nivel_filter.lower()
                mask = vagas_filtradas['nivel_profissional'].str.lower().str.contains(nivel_filter_lower, na=False)
                vagas_filtradas = vagas_filtradas[mask]
            
            # Calcular paginação
            total_vagas = len(vagas_filtradas)
            total_pages = (total_vagas + per_page - 1) // per_page  # Ceiling division
            
            # Validar página
            if page < 1:
                page = 1
            elif page > total_pages and total_pages > 0:
                page = total_pages
            
            # Calcular offset
            offset = (page - 1) * per_page
            
            # Pegar vagas da página atual
            vagas_pagina = vagas_filtradas.iloc[offset:offset + per_page]
            
            # Preparar dados das vagas para exibição
            required_columns = ['id_vaga', 'titulo_vaga', 'cliente', 'nivel_profissional', 'areas_atuacao', 'cidade']
            available_columns = [col for col in required_columns if col in vagas_pagina.columns]
            
            if not available_columns:
                return "Erro: Colunas necessárias não encontradas nos dados", 500
            
            vagas_display = vagas_pagina[available_columns].fillna('').to_dict('records')
            
            # Buscar níveis únicos para o filtro
            niveis_unicos = sorted(df_vagas['nivel_profissional'].dropna().unique())
        
        # Informações de paginação
        pagination_info = {
            'current_page': page,
            'total_pages': total_pages,
            'total_vagas': total_vagas,
            'per_page': per_page,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None,
            'pages': list(range(max(1, page - 2), min(total_pages + 1, page + 3)))
        }
        
        return render_template('index.html', 
                             vagas=vagas_display,
                             pagination=pagination_info,
                             search=search,
                             nivel_filter=nivel_filter,
                             niveis_disponiveis=niveis_unicos)
                             
    except Exception as e:
        return f"Erro ao processar dados das vagas: {str(e)}", 500

@app.route('/status')
def status_page():
    """Página de status do sistema"""
    return render_template('status.html')

@app.route('/api/stats')
def api_stats():
    """Endpoint para estatísticas do sistema usando PostgreSQL"""
    try:
        # Verificar se PostgreSQL está disponível
        if is_postgres_available():
            # Buscar estatísticas do PostgreSQL
            try:
                engine = create_pg_engine()
                with engine.connect() as conn:
                    # Contar vagas
                    result_vagas = conn.execute(text("SELECT COUNT(*) FROM vagas"))
                    total_vagas = result_vagas.scalar() or 0
                    
                    # Contar vagas com prospects
                    result_prospects = conn.execute(text("SELECT COUNT(DISTINCT id_vaga) FROM prospects"))
                    vagas_com_prospects_count = result_prospects.scalar() or 0
                    
                    # Contar candidatos
                    result_candidatos = conn.execute(text("SELECT COUNT(*) FROM candidatos"))
                    total_candidatos = result_candidatos.scalar() or 0
                    
                stats = {
                    'total_vagas': total_vagas,
                    'vagas_com_prospects': vagas_com_prospects_count,
                    'total_candidatos': total_candidatos,
                    'modelo_carregado': pipeline_model is not None,
                    'postgres_available': True
                }
            except Exception as e:
                print(f"❌ Erro ao buscar estatísticas do PostgreSQL: {e}")
                # Fallback para dados em memória
                stats = {
                    'total_vagas': len(df_vagas) if df_vagas is not None else 0,
                    'vagas_com_prospects': len(vagas_com_prospects),
                    'total_candidatos': len(df_candidates) if df_candidates is not None else 0,
                    'modelo_carregado': pipeline_model is not None,
                    'postgres_available': False,
                    'error': str(e)
                }
        else:
            # Usar dados em memória quando PostgreSQL não está disponível
            stats = {
                'total_vagas': len(df_vagas) if df_vagas is not None else 0,
                'vagas_com_prospects': len(vagas_com_prospects),
                'total_candidatos': len(df_candidates) if df_candidates is not None else 0,
                'modelo_carregado': pipeline_model is not None,
                'postgres_available': False
            }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vaga/<id_vaga>')
def vaga_detalhes(id_vaga):
    """Página de detalhes da vaga com candidatos compatíveis usando modelo aprimorado"""
    if df_vagas is None or df_vagas.empty:
        return "Erro: Dados de vagas não carregados", 500
    
    if df_candidates is None or df_candidates.empty:
        return "Erro: Dados de candidatos não carregados", 500
        
    if pipeline_model is None:
        return "Erro: Modelo ML não carregado", 500
    
    try:
        # Buscar informações da vaga
        vaga_info = df_vagas[df_vagas['id_vaga'] == id_vaga]
        if vaga_info.empty:
            return "Vaga não encontrada", 404
        
        vaga_row = vaga_info.iloc[0]
        
        # Calcular compatibilidade com todos os candidatos usando modelo aprimorado
        candidatos_com_score = []
        
        for _, candidate_row in df_candidates.iterrows():
            try:
                # Preparar features avançadas
                prediction_data = prepare_enhanced_features(vaga_row, candidate_row)
                
                # Fazer predição com modelo aprimorado
                probability = pipeline_model.predict_proba(prediction_data)[0]
                match_score = probability[1] if len(probability) > 1 else 0.5
                
                candidato_info = {
                    'codigo_candidato': candidate_row['codigo_candidato'],
                    'nome': candidate_row['nome'],
                    'email': candidate_row['email'],
                    'telefone': candidate_row['telefone'],
                    'nivel_academico': candidate_row['nivel_academico'],
                    'area_de_atuacao': candidate_row['area_de_atuacao'],
                    'match_score': round(match_score * 100, 2)
                }
                candidatos_com_score.append(candidato_info)
                
            except Exception as e:
                print(f"Erro ao processar candidato {candidate_row['codigo_candidato']}: {e}")
                continue
        
        # Ordenar por score de compatibilidade
        candidatos_com_score.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Preparar informações da vaga para exibição
        vaga_display = {
            'id_vaga': vaga_row['id_vaga'],
            'titulo_vaga': vaga_row['titulo_vaga'],
            'cliente': vaga_row['cliente'],
            'nivel_profissional': vaga_row['nivel_profissional'],
            'areas_atuacao': vaga_row['areas_atuacao'],
            'cidade': vaga_row['cidade'],
            'tipo_contratacao': vaga_row['tipo_contratacao'],
            'competencias_tecnicas_requeridas': str(vaga_row['competencias_tecnicas_requeridas'])[:500] + '...' if len(str(vaga_row['competencias_tecnicas_requeridas'])) > 500 else str(vaga_row['competencias_tecnicas_requeridas'])
        }
        
        return render_template('vaga_detalhes.html', 
                             vaga=vaga_display, 
                             candidatos=candidatos_com_score)
                             
    except Exception as e:
        return f"Erro ao processar detalhes da vaga: {str(e)}", 500

@app.route('/api/predict', methods=['POST'])
def predict():
    """Endpoint para predições via API usando modelo aprimorado"""
    try:
        if pipeline_model is None:
            return jsonify({'error': 'Modelo aprimorado não carregado'}), 500
        
        data = request.get_json()
        
        # Validar campos obrigatórios do modelo aprimorado
        required_fields = ['tech_match_score', 'nivel_profissional', 'areas_atuacao', 
                         'area_de_atuacao', 'academic_match', 'english_match', 'combined_text']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Preparar dados para predição
        prediction_data = pd.DataFrame([data])
        
        # Fazer predição
        prediction = pipeline_model.predict(prediction_data)[0]
        probability = pipeline_model.predict_proba(prediction_data)[0]
        
        result = {
            'prediction': int(prediction),
            'prediction_text': 'CONTRATADO' if prediction == 1 else 'NÃO CONTRATADO',
            'probability': {
                'not_hired': float(probability[0]),
                'hired': float(probability[1]) if len(probability) > 1 else 0.0
            },
            'match_score': float(probability[1] * 100) if len(probability) > 1 else 50.0,
            'model_type': 'enhanced',
            'explanation': {
                'tech_compatibility': f"{data['tech_match_score']*100:.1f}%",
                'academic_match': data['academic_match'],
                'english_match': data['english_match']
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict_auto', methods=['POST'])
def predict_auto():
    """Endpoint que calcula automaticamente as features avançadas a partir de dados básicos"""
    try:
        if pipeline_model is None:
            return jsonify({'error': 'Modelo aprimorado não carregado'}), 500
        
        data = request.get_json()
        
        # Campos obrigatórios mínimos
        required_fields = ['nivel_profissional', 'areas_atuacao', 'area_de_atuacao']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        # Calcular features automaticamente
        def safe_calculate_tech_match():
            comp_req = data.get('competencias_tecnicas_requeridas', '')
            conhecimentos = data.get('conhecimentos_tecnicos', '')
            if not comp_req or not conhecimentos:
                return 0.3  # Score médio quando não há dados
            
            comp_words = set(str(comp_req).lower().split())
            conhec_words = set(str(conhecimentos).lower().split())
            if len(comp_words) == 0:
                return 0.3
            return len(comp_words.intersection(conhec_words)) / len(comp_words)
        
        # Preparar dados completos para o modelo aprimorado
        enhanced_data = {
            'tech_match_score': safe_calculate_tech_match(),
            'nivel_profissional': data['nivel_profissional'],
            'areas_atuacao': data['areas_atuacao'],
            'area_de_atuacao': data['area_de_atuacao'],
            'academic_match': data.get('academic_match', 'indefinido'),
            'english_match': data.get('english_match', 'indefinido'),
            'combined_text': ' '.join([
                str(data.get('competencias_tecnicas_requeridas', '')),
                str(data.get('conhecimentos_tecnicos', '')),
                str(data.get('principais_atividades', '')),
                str(data.get('area_de_atuacao', ''))
            ]).lower().strip() or 'sem informações adicionais'
        }
        
        # Fazer predição
        prediction_data = pd.DataFrame([enhanced_data])
        prediction = pipeline_model.predict(prediction_data)[0]
        probability = pipeline_model.predict_proba(prediction_data)[0]
        
        result = {
            'prediction': int(prediction),
            'prediction_text': 'CONTRATADO' if prediction == 1 else 'NÃO CONTRATADO',
            'probability': {
                'not_hired': float(probability[0]),
                'hired': float(probability[1]) if len(probability) > 1 else 0.0
            },
            'match_score': float(probability[1] * 100) if len(probability) > 1 else 50.0,
            'model_type': 'enhanced_auto',
            'features_calculated': enhanced_data,
            'explanation': {
                'tech_compatibility': f"{enhanced_data['tech_match_score']*100:.1f}%",
                'academic_match': enhanced_data['academic_match'],
                'english_match': enhanced_data['english_match']
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    status = {
        'status': 'healthy',
        'model_type': 'enhanced',
        'model_loaded': pipeline_model is not None,
        'vagas_loaded': df_vagas is not None and not df_vagas.empty,
        'candidates_loaded': df_candidates is not None and not df_candidates.empty
    }
    return jsonify(status)

@app.route('/model/info')
def model_info():
    """Informações sobre o modelo em uso"""
    try:
        # Carregar metadados do modelo aprimorado
        metadata_path = os.path.join(BASE_DIR, 'models', 'model_metadata_enhanced.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            metadata = {'model_type': 'enhanced', 'features': 7}
        
        return jsonify({
            'model_type': 'enhanced',
            'model_loaded': pipeline_model is not None,
            'model_path': os.path.join(BASE_DIR, 'models', 'pipeline_aprimorado.joblib'),
            'metadata': metadata
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    load_resources()
    app.run(host='0.0.0.0', port=5000, debug=False)

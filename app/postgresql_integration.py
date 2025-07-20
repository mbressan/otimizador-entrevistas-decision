#!/usr/bin/env python3
# Integração PostgreSQL para Otimizador de Entrevistas

import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine, text
from pathlib import Path

# Configurações do PostgreSQL
PG_CONFIG = {
    'host': os.getenv('DB_HOST', 'postgresql'),
    'database': os.getenv('DB_NAME', 'otimizador_entrevistas'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def create_pg_engine():
    """Cria engine SQLAlchemy para PostgreSQL"""
    connection_string = f"postgresql://{PG_CONFIG['user']}:{PG_CONFIG['password']}@{PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}"
    return create_engine(connection_string, pool_pre_ping=True, pool_recycle=300)

def is_postgres_available():
    """Verifica se o PostgreSQL está disponível"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            return True
    except Exception as e:
        print(f"❌ PostgreSQL não disponível: {e}")
        return False

def create_database_schema():
    """Cria as tabelas do banco PostgreSQL"""
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor()
        
        print("📋 Criando tabelas PostgreSQL...")
        
        # Tabela de Vagas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vagas (
            id_vaga VARCHAR(50) PRIMARY KEY,
            titulo_vaga TEXT,
            cliente VARCHAR(200),
            tipo_contratacao VARCHAR(100),
            nivel_profissional VARCHAR(50),
            nivel_academico VARCHAR(50),
            nivel_ingles VARCHAR(50),
            areas_atuacao TEXT,
            competencias_tecnicas_requeridas TEXT,
            principais_atividades TEXT,
            pais VARCHAR(100),
            estado VARCHAR(100),
            cidade VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabela de Candidatos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidatos (
            codigo_candidato VARCHAR(50) PRIMARY KEY,
            nome VARCHAR(200),
            email VARCHAR(200),
            telefone VARCHAR(50),
            data_nascimento VARCHAR(20),
            estado_civil VARCHAR(50),
            pcd VARCHAR(10),
            nivel_academico VARCHAR(50),
            area_formacao VARCHAR(200),
            nivel_ingles VARCHAR(50),
            conhecimentos_tecnicos TEXT,
            area_de_atuacao VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabela de Prospects (histórico de candidaturas)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prospects (
            id SERIAL PRIMARY KEY,
            id_vaga VARCHAR(50),
            codigo_candidato VARCHAR(50),
            nome_candidato VARCHAR(200),
            situacao_candidado VARCHAR(200),
            data_candidatura VARCHAR(20),
            comentario TEXT,
            recrutador VARCHAR(200),
            contratado INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_vaga) REFERENCES vagas(id_vaga) ON DELETE CASCADE,
            FOREIGN KEY (codigo_candidato) REFERENCES candidatos(codigo_candidato) ON DELETE CASCADE
        )
        ''')
        
        # Tabela de Predições (log das predições do ML)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS predicoes (
            id SERIAL PRIMARY KEY,
            id_vaga VARCHAR(50),
            codigo_candidato VARCHAR(50),
            tech_match_score REAL,
            academic_match VARCHAR(50),
            english_match VARCHAR(50),
            probabilidade_contratacao REAL,
            predicao_contratado INTEGER,
            modelo_versao VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_vaga) REFERENCES vagas(id_vaga) ON DELETE CASCADE,
            FOREIGN KEY (codigo_candidato) REFERENCES candidatos(codigo_candidato) ON DELETE CASCADE
        )
        ''')
        
        # Índices otimizados para PostgreSQL
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vagas_nivel ON vagas(nivel_profissional)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_vagas_areas ON vagas USING gin(to_tsvector(\'portuguese\', areas_atuacao))')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_candidatos_area ON candidatos USING gin(to_tsvector(\'portuguese\', area_de_atuacao))')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prospects_vaga ON prospects(id_vaga)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prospects_candidato ON prospects(codigo_candidato)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prospects_contratado ON prospects(contratado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predicoes_vaga ON predicoes(id_vaga)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predicoes_data ON predicoes(created_at)')
        
        # Views úteis para PostgreSQL
        cursor.execute('''
        CREATE OR REPLACE VIEW vw_vagas_stats AS
        SELECT 
            v.id_vaga,
            v.titulo_vaga,
            v.cliente,
            v.nivel_profissional,
            v.areas_atuacao,
            COUNT(p.codigo_candidato) as total_candidatos,
            SUM(p.contratado) as total_contratados,
            CASE 
                WHEN COUNT(p.codigo_candidato) > 0 
                THEN ROUND(AVG(p.contratado) * 100, 2) 
                ELSE 0 
            END as taxa_contratacao
        FROM vagas v
        LEFT JOIN prospects p ON v.id_vaga = p.id_vaga
        GROUP BY v.id_vaga, v.titulo_vaga, v.cliente, v.nivel_profissional, v.areas_atuacao
        ''')
        
        cursor.execute('''
        CREATE OR REPLACE VIEW vw_candidatos_ranking AS
        SELECT 
            c.codigo_candidato,
            c.nome,
            c.area_de_atuacao,
            c.nivel_academico,
            COUNT(p.id_vaga) as total_candidaturas,
            SUM(p.contratado) as total_contratacoes,
            CASE 
                WHEN COUNT(p.id_vaga) > 0 
                THEN ROUND(AVG(p.contratado) * 100, 2) 
                ELSE 0 
            END as taxa_sucesso
        FROM candidatos c
        LEFT JOIN prospects p ON c.codigo_candidato = p.codigo_candidato
        GROUP BY c.codigo_candidato, c.nome, c.area_de_atuacao, c.nivel_academico
        ''')
        
        conn.commit()
        print("✅ Esquema PostgreSQL criado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar esquema PostgreSQL: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def load_json_data(file_path):
    """Carrega dados de um arquivo JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        return {}

def normalize_vagas(vagas_data):
    """Normaliza os dados das vagas para um formato estruturado"""
    vagas_list = []
    
    for vaga_id, vaga_info in vagas_data.items():
        try:
            basic_info = vaga_info.get('informacoes_basicas', {})
            profile_info = vaga_info.get('perfil_vaga', {})
            
            normalized_vaga = {
                'id_vaga': vaga_id,
                'titulo_vaga': basic_info.get('titulo_vaga', ''),
                'cliente': basic_info.get('cliente', ''),
                'tipo_contratacao': basic_info.get('tipo_contratacao', ''),
                'nivel_profissional': profile_info.get('nivel profissional', ''),
                'nivel_academico': profile_info.get('nivel_academico', ''),
                'nivel_ingles': profile_info.get('nivel_ingles', ''),
                'areas_atuacao': profile_info.get('areas_atuacao', ''),
                'competencias_tecnicas_requeridas': profile_info.get('competencia_tecnicas_e_comportamentais', ''),
                'principais_atividades': profile_info.get('principais_atividades', ''),
                'pais': profile_info.get('pais', ''),
                'estado': profile_info.get('estado', ''),
                'cidade': profile_info.get('cidade', '')
            }
            vagas_list.append(normalized_vaga)
        except Exception as e:
            print(f"Erro ao processar vaga {vaga_id}: {e}")
            continue
    
    return pd.DataFrame(vagas_list)

def normalize_applicants(applicants_data):
    """Normaliza os dados dos candidatos"""
    applicants_list = []
    
    for candidate_id, candidate_info in applicants_data.items():
        try:
            basic_info = candidate_info.get('infos_basicas', {})
            personal_info = candidate_info.get('informacoes_pessoais', {})
            academic_info = candidate_info.get('formacao_academica', {})
            professional_info = candidate_info.get('informacoes_profissionais', {})
            
            normalized_candidate = {
                'codigo_candidato': candidate_id,
                'nome': basic_info.get('nome', ''),
                'email': basic_info.get('email', ''),
                'telefone': basic_info.get('telefone', ''),
                'data_nascimento': personal_info.get('data_nascimento', ''),
                'estado_civil': personal_info.get('estado_civil', ''),
                'pcd': personal_info.get('pcd', ''),
                'nivel_academico': academic_info.get('nivel_academico', '') if academic_info else '',
                'area_formacao': academic_info.get('area_formacao', '') if academic_info else '',
                'nivel_ingles': professional_info.get('nivel_ingles', '') if professional_info else '',
                'conhecimentos_tecnicos': professional_info.get('conhecimentos_tecnicos', '') if professional_info else '',
                'area_de_atuacao': professional_info.get('area_atuacao', '') if professional_info else ''
            }
            applicants_list.append(normalized_candidate)
        except Exception as e:
            print(f"Erro ao processar candidato {candidate_id}: {e}")
            continue
    
    return pd.DataFrame(applicants_list)

def process_prospects(prospects_data):
    """Processa os dados de prospects para extrair pares candidato-vaga com situação"""
    prospects_list = []
    
    for vaga_id, vaga_prospect in prospects_data.items():
        vaga_titulo = vaga_prospect.get('titulo', '')
        prospects = vaga_prospect.get('prospects', [])
        
        for prospect in prospects:
            try:
                # Extrair código do candidato (remover prefixos se existirem)
                codigo_candidato = prospect.get('codigo', '').strip()
                situacao = prospect.get('situacao_candidato', '').strip()
                
                prospect_record = {
                    'id_vaga': vaga_id,
                    'codigo_candidato': codigo_candidato,
                    'nome_candidato': prospect.get('nome', ''),
                    'situacao_candidato': situacao,
                    'data_candidatura': prospect.get('data_candidatura', ''),
                    'comentario': prospect.get('comentario', ''),
                    'recrutador': prospect.get('recrutador', ''),
                    # Criar variável alvo binária
                    'contratado': 1 if 'Contratado pela Decision' in situacao else 0
                }
                prospects_list.append(prospect_record)
            except Exception as e:
                print(f"Erro ao processar prospect da vaga {vaga_id}: {e}")
                continue
    
    return pd.DataFrame(prospects_list)

def migrate_data_to_postgresql():
    """Migra os dados dos arquivos JSON para o banco PostgreSQL"""
    
    try:
        engine = create_pg_engine()
        
        print("🚀 Migrando dados para PostgreSQL...")
        
        # Verificar se já existem dados
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM vagas")).fetchone()
            vagas_count = result[0]
        
        if vagas_count > 0:
            print(f"⚠️  Banco já contém {vagas_count} vagas. Pulando migração.")
            return True
        
        # Carregar dados JSON
        data_path = Path(__file__).parent.parent / "data"
        
        vagas_path = data_path / "vagas.json"
        applicants_path = data_path / "applicants.json"
        prospects_path = data_path / "prospects.json"
        
        print("📂 Carregando arquivos JSON...")
        vagas_data = load_json_data(vagas_path)
        applicants_data = load_json_data(applicants_path)
        prospects_data = load_json_data(prospects_path)
        
        print(f"Vagas carregadas: {len(vagas_data)}")
        print(f"Candidatos carregados: {len(applicants_data)}")
        print(f"Prospects carregados: {len(prospects_data)}")
        
        # Processar dados
        print("🔄 Processando dados...")
        df_vagas = normalize_vagas(vagas_data)
        df_candidates = normalize_applicants(applicants_data)
        df_prospects = process_prospects(prospects_data)
        
        # 1. Migrar Vagas
        print("📋 Migrando vagas para PostgreSQL...")
        df_vagas_clean = df_vagas.fillna('')
        
        rows_inserted = df_vagas_clean.to_sql(
            'vagas', 
            engine, 
            if_exists='append', 
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ {len(df_vagas)} vagas migradas")
        
        # 2. Migrar Candidatos
        print("👥 Migrando candidatos para PostgreSQL...")
        df_candidates_clean = df_candidates.fillna('')
        
        rows_inserted = df_candidates_clean.to_sql(
            'candidatos', 
            engine, 
            if_exists='append', 
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ {len(df_candidates)} candidatos migrados")
        
        # 3. Migrar Prospects
        print("🎯 Migrando prospects para PostgreSQL...")
        df_prospects_clean = df_prospects.fillna('')
        
        rows_inserted = df_prospects_clean.to_sql(
            'prospects', 
            engine, 
            if_exists='append', 
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ {len(df_prospects)} prospects migrados")
        
        # Verificar migração
        with engine.connect() as conn:
            vagas_df = pd.read_sql("SELECT COUNT(*) as count FROM vagas", conn)
            candidatos_df = pd.read_sql("SELECT COUNT(*) as count FROM candidatos", conn)
            prospects_df = pd.read_sql("SELECT COUNT(*) as count FROM prospects", conn)
            contratados_df = pd.read_sql("SELECT COUNT(*) as count FROM prospects WHERE contratado = 1", conn)
            
            vagas_db = vagas_df['count'].iloc[0]
            candidatos_db = candidatos_df['count'].iloc[0]
            prospects_db = prospects_df['count'].iloc[0]
            contratados_db = contratados_df['count'].iloc[0]
        
        print(f"\n📊 RESUMO DA MIGRAÇÃO POSTGRESQL:")
        print(f"   Vagas no banco: {vagas_db:,}")
        print(f"   Candidatos no banco: {candidatos_db:,}")
        print(f"   Prospects no banco: {prospects_db:,}")
        print(f"   Contratados: {contratados_db:,}")
        print(f"   Taxa de contratação: {contratados_db/prospects_db:.2%}")
        
        print(f"\n🎉 Migração PostgreSQL concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração PostgreSQL: {e}")
        import traceback
        traceback.print_exc()
        return False

def setup_postgres_database():
    """Configura o banco PostgreSQL criando esquema e migrando dados"""
    try:
        # Criar esquema
        if not create_database_schema():
            return False
        
        # Migrar dados
        if not migrate_data_to_postgresql():
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração do PostgreSQL: {e}")
        return False

def load_vagas_from_postgres():
    """Carrega vagas do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM vagas", conn)
            return df.to_dict('index')
    except Exception as e:
        print(f"❌ Erro ao carregar vagas do PostgreSQL: {e}")
        return {}

def load_candidatos_from_postgres():
    """Carrega candidatos do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM candidatos", conn)
            return df.to_dict('records')
    except Exception as e:
        print(f"❌ Erro ao carregar candidatos do PostgreSQL: {e}")
        return []

def load_prospects_from_postgres():
    """Carrega prospects do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM prospects", conn)
            
            # Agrupar por vaga
            prospects_dict = {}
            for _, row in df.iterrows():
                vaga_id = row['id_vaga']
                if vaga_id not in prospects_dict:
                    prospects_dict[vaga_id] = {'prospects': []}
                
                prospect = {
                    'codigo': row['codigo_candidato'],
                    'nome': row['nome_candidato'],
                    'situacao_candidato': row['situacao_candidato'],
                    'data_candidatura': row['data_candidatura'],
                    'comentario': row['comentario'],
                    'recrutador': row['recrutador']
                }
                prospects_dict[vaga_id]['prospects'].append(prospect)
            
            return prospects_dict
    except Exception as e:
        print(f"❌ Erro ao carregar prospects do PostgreSQL: {e}")
        return {}

def search_vagas_postgres(search_term='', nivel_filter='', page=1, per_page=10):
    """Busca vagas no PostgreSQL com paginação e filtros"""
    try:
        engine = create_pg_engine()
        
        # Construir query base
        base_query = """
        SELECT DISTINCT v.*, 
               COUNT(p.codigo_candidato) as total_candidatos,
               SUM(p.contratado) as total_contratados
        FROM vagas v
        LEFT JOIN prospects p ON v.id_vaga = p.id_vaga
        WHERE 1=1
        """
        
        params = []
        
        # Adicionar filtros
        if search_term:
            base_query += """
            AND (
                to_tsvector('portuguese', v.titulo_vaga) @@ plainto_tsquery('portuguese', %s) OR
                to_tsvector('portuguese', v.cliente) @@ plainto_tsquery('portuguese', %s) OR
                to_tsvector('portuguese', v.areas_atuacao) @@ plainto_tsquery('portuguese', %s)
            )
            """
            params.extend([search_term, search_term, search_term])
        
        if nivel_filter:
            base_query += " AND LOWER(v.nivel_profissional) = LOWER(%s)"
            params.append(nivel_filter)
        
        # Agrupar e ordenar
        base_query += """
        GROUP BY v.id_vaga, v.titulo_vaga, v.cliente, v.nivel_profissional, v.areas_atuacao
        HAVING COUNT(p.codigo_candidato) > 0
        ORDER BY v.titulo_vaga
        """
        
        # Query para contar total
        count_query = f"""
        SELECT COUNT(*) FROM (
            {base_query}
        ) as subquery
        """
        
        # Query para dados paginados
        data_query = f"""
        {base_query}
        LIMIT %s OFFSET %s
        """
        
        with engine.connect() as conn:
            # Contar total
            result = conn.execute(text(count_query), params)
            total = result.fetchone()[0]
            
            # Calcular paginação
            total_pages = (total + per_page - 1) // per_page
            offset = (page - 1) * per_page
            
            # Buscar dados
            params_with_pagination = params + [per_page, offset]
            result = conn.execute(text(data_query), params_with_pagination)
            
            vagas = []
            for row in result:
                vaga = {
                    'id_vaga': row[0],
                    'titulo_vaga': row[1],
                    'cliente': row[2],
                    'tipo_contratacao': row[3],
                    'nivel_profissional': row[4],
                    'nivel_academico': row[5],
                    'nivel_ingles': row[6],
                    'areas_atuacao': row[7],
                    'competencias_tecnicas_requeridas': row[8],
                    'principais_atividades': row[9],
                    'pais': row[10],
                    'estado': row[11],
                    'cidade': row[12],
                    'total_candidatos': row[13] or 0,
                    'total_contratados': row[14] or 0
                }
                vagas.append(vaga)
            
            # Buscar níveis únicos para filtros
            niveis_query = """
            SELECT DISTINCT nivel_profissional 
            FROM vagas 
            WHERE nivel_profissional != '' AND nivel_profissional IS NOT NULL
            ORDER BY nivel_profissional
            """
            niveis_result = conn.execute(text(niveis_query))
            niveis_unicos = [row[0] for row in niveis_result]
            
            return {
                'vagas': vagas,
                'total': total,
                'total_pages': total_pages,
                'current_page': page,
                'niveis_unicos': niveis_unicos
            }
            
    except Exception as e:
        print(f"❌ Erro na busca PostgreSQL: {e}")
        return {
            'vagas': [],
            'total': 0,
            'total_pages': 0,
            'current_page': page,
            'niveis_unicos': []
        }

def save_predicao_to_postgres(id_vaga, codigo_candidato, tech_match_score, academic_match, 
                             english_match, probabilidade_contratacao, predicao_contratado, modelo_versao):
    """Salva uma predição no PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            INSERT INTO predicoes (id_vaga, codigo_candidato, tech_match_score, academic_match, 
                                  english_match, probabilidade_contratacao, predicao_contratado, modelo_versao)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            conn.execute(text(query), [
                id_vaga, codigo_candidato, tech_match_score, academic_match,
                english_match, probabilidade_contratacao, predicao_contratado, modelo_versao
            ])
            conn.commit()
            return True
    except Exception as e:
        print(f"❌ Erro ao salvar predição: {e}")
        return False

def get_vagas_stats_postgres():
    """Obtém estatísticas das vagas do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT 
                COUNT(*) as total_vagas,
                COUNT(DISTINCT id_vaga) as vagas_com_prospects
            FROM vagas
            """
            result = conn.execute(text(query))
            row = result.fetchone()
            return {
                'total_vagas': row[0],
                'vagas_com_prospects': row[1]
            }
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas das vagas: {e}")
        return {'total_vagas': 0, 'vagas_com_prospects': 0}

def get_candidatos_stats_postgres():
    """Obtém estatísticas dos candidatos do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT 
                COUNT(*) as total_candidatos,
                COUNT(DISTINCT codigo_candidato) as candidatos_unicos
            FROM candidatos
            """
            result = conn.execute(text(query))
            row = result.fetchone()
            return {
                'total_candidatos': row[0],
                'candidatos_unicos': row[1]
            }
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas dos candidatos: {e}")
        return {'total_candidatos': 0, 'candidatos_unicos': 0}

def get_prospects_stats_postgres():
    """Obtém estatísticas dos prospects do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT 
                COUNT(*) as total_prospects,
                SUM(contratado) as total_contratados,
                CASE 
                    WHEN COUNT(*) > 0 
                    THEN ROUND(AVG(contratado) * 100, 2) 
                    ELSE 0 
                END as taxa_contratacao
            FROM prospects
            """
            result = conn.execute(text(query))
            row = result.fetchone()
            return {
                'total_prospects': row[0],
                'total_contratados': row[1] or 0,
                'taxa_contratacao': row[2] or 0
            }
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas dos prospects: {e}")
        return {'total_prospects': 0, 'total_contratados': 0, 'taxa_contratacao': 0}

def get_predicoes_stats_postgres():
    """Obtém estatísticas das predições do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT 
                COUNT(*) as total_predicoes,
                AVG(probabilidade_contratacao) as media_probabilidade,
                COUNT(CASE WHEN predicao_contratado = 1 THEN 1 END) as predicoes_positivas
            FROM predicoes
            """
            result = conn.execute(text(query))
            row = result.fetchone()
            return {
                'total_predicoes': row[0],
                'media_probabilidade': row[1] or 0,
                'predicoes_positivas': row[2] or 0
            }
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas das predições: {e}")
        return {'total_predicoes': 0, 'media_probabilidade': 0, 'predicoes_positivas': 0}

def get_estados_postgres():
    """Obtém lista de estados únicos do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT DISTINCT estado 
            FROM vagas 
            WHERE estado != '' AND estado IS NOT NULL
            ORDER BY estado
            """
            result = conn.execute(text(query))
            return [row[0] for row in result]
    except Exception as e:
        print(f"❌ Erro ao obter estados: {e}")
        return []

def get_cidades_postgres():
    """Obtém lista de cidades únicas do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT DISTINCT cidade 
            FROM vagas 
            WHERE cidade != '' AND cidade IS NOT NULL
            ORDER BY cidade
            """
            result = conn.execute(text(query))
            return [row[0] for row in result]
    except Exception as e:
        print(f"❌ Erro ao obter cidades: {e}")
        return []

def get_clientes_postgres():
    """Obtém lista de clientes únicos do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT DISTINCT cliente 
            FROM vagas 
            WHERE cliente != '' AND cliente IS NOT NULL
            ORDER BY cliente
            """
            result = conn.execute(text(query))
            return [row[0] for row in result]
    except Exception as e:
        print(f"❌ Erro ao obter clientes: {e}")
        return []

def get_niveis_profissionais_postgres():
    """Obtém lista de níveis profissionais únicos do PostgreSQL"""
    try:
        engine = create_pg_engine()
        with engine.connect() as conn:
            query = """
            SELECT DISTINCT nivel_profissional 
            FROM vagas 
            WHERE nivel_profissional != '' AND nivel_profissional IS NOT NULL
            ORDER BY nivel_profissional
            """
            result = conn.execute(text(query))
            return [row[0] for row in result]
    except Exception as e:
        print(f"❌ Erro ao obter níveis profissionais: {e}")
        return []

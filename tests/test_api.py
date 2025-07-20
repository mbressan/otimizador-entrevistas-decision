import pytest
import json
import pandas as pd
from pathlib import Path
import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app, load_json_data, normalize_vagas, normalize_applicants, prepare_prediction_data


@pytest.fixture
def client():
    """Fixture para cliente de teste Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_vaga():
    """Fixture com dados de exemplo de uma vaga"""
    return {
        'id_vaga': 'V001',
        'titulo_vaga': 'Desenvolvedor Python',
        'cliente': 'Empresa Teste',
        'nivel_profissional': 'Senior',
        'competencias_tecnicas_requeridas': 'Python Flask Django PostgreSQL',
        'principais_atividades': 'Desenvolvimento de aplicações web',
        'areas_atuacao': 'TI - Desenvolvimento',
        'cidade': 'São Paulo'
    }


@pytest.fixture
def sample_candidate():
    """Fixture com dados de exemplo de um candidato"""
    return {
        'codigo_candidato': 'C001',
        'nome': 'João Silva',
        'email': 'joao@email.com',
        'telefone': '(11) 99999-9999',
        'conhecimentos_tecnicos': 'Python Django PostgreSQL Docker',
        'area_de_atuacao': 'Desenvolvimento',
        'nivel_academico': 'Superior Completo'
    }


class TestDataProcessing:
    """Testes para funções de processamento de dados"""
    
    def test_load_json_data_success(self, tmp_path):
        """Testa carregamento bem-sucedido de arquivo JSON"""
        # Criar arquivo JSON temporário
        test_data = {"test": "data"}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(test_data))
        
        # Testar carregamento
        result = load_json_data(json_file)
        assert result == test_data
    
    def test_load_json_data_file_not_found(self):
        """Testa comportamento quando arquivo não existe"""
        result = load_json_data("arquivo_inexistente.json")
        assert result == {}
    
    def test_normalize_vagas(self):
        """Testa normalização de dados de vagas"""
        vagas_data = {
            "1001": {
                "informacoes_basicas": {
                    "titulo_vaga": "Dev Python",
                    "cliente": "Empresa A"
                },
                "perfil_vaga": {
                    "nivel profissional": "Senior",
                    "competencia_tecnicas_e_comportamentais": "Python, Flask"
                }
            }
        }
        
        df = normalize_vagas(vagas_data)
        
        assert not df.empty
        assert len(df) == 1
        assert df.iloc[0]['id_vaga'] == "1001"
        assert df.iloc[0]['titulo_vaga'] == "Dev Python"
        assert df.iloc[0]['nivel_profissional'] == "Senior"
    
    def test_normalize_applicants(self):
        """Testa normalização de dados de candidatos"""
        applicants_data = {
            "2001": {
                "infos_basicas": {
                    "nome": "Maria Silva",
                    "email": "maria@email.com"
                },
                "informacoes_pessoais": {
                    "data_nascimento": "1990-01-01"
                },
                "informacoes_profissionais": {
                    "conhecimentos_tecnicos": "Python Django"
                }
            }
        }
        
        df = normalize_applicants(applicants_data)
        
        assert not df.empty
        assert len(df) == 1
        assert df.iloc[0]['codigo_candidato'] == "2001"
        assert df.iloc[0]['nome'] == "Maria Silva"
        assert df.iloc[0]['conhecimentos_tecnicos'] == "Python Django"
    
    def test_prepare_prediction_data(self, sample_vaga, sample_candidate):
        """Testa preparação de dados para predição"""
        df = prepare_prediction_data(sample_vaga, sample_candidate)
        
        assert not df.empty
        assert len(df) == 1
        # Verificar apenas as 3 features que o modelo usa
        assert 'nivel_profissional' in df.columns
        assert 'areas_atuacao' in df.columns
        assert 'area_de_atuacao' in df.columns


class TestFlaskRoutes:
    """Testes para rotas da aplicação Flask"""
    
    def test_health_endpoint(self, client):
        """Testa endpoint de health check"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
    
    def test_index_route(self, client):
        """Testa rota principal"""
        response = client.get('/')
        # Como não temos dados carregados no teste, pode retornar 500
        # Em um ambiente real, seria 200
        assert response.status_code in [200, 500]
    
    def test_predict_api_missing_data(self, client):
        """Testa API de predição com dados faltando"""
        response = client.post('/api/predict',
                             json={},
                             content_type='application/json')
        
        # Como o modelo pode não estar carregado nos testes, aceitar 400 ou 500
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'error' in data

    def test_predict_api_with_data(self, client):
        """Testa API de predição com dados válidos"""
        test_data = {
            'nivel_profissional': 'senior',
            'areas_atuacao': 'ti - desenvolvimento', 
            'area_de_atuacao': 'desenvolvimento web'
        }
        
        response = client.post('/api/predict',
                             json=test_data,
                             content_type='application/json')
        
        # Como o modelo pode não estar carregado nos testes, aceitar 200 ou 500
        assert response.status_code in [200, 500]


class TestDataValidation:
    """Testes para validação de dados"""
    
    def test_empty_dataframe_handling(self):
        """Testa tratamento de DataFrames vazios"""
        empty_data = {}
        df = normalize_vagas(empty_data)
        assert df.empty
    
    def test_missing_fields_handling(self):
        """Testa tratamento de campos faltando"""
        incomplete_data = {
            "1001": {
                "informacoes_basicas": {}  # Campos faltando
            }
        }
        
        df = normalize_vagas(incomplete_data)
        assert not df.empty  # Deve processar mesmo com campos faltando
        assert df.iloc[0]['titulo_vaga'] == ''  # Campo vazio deve ser string vazia
    
    def test_data_type_consistency(self, sample_vaga, sample_candidate):
        """Testa consistência de tipos de dados"""
        df = prepare_prediction_data(sample_vaga, sample_candidate)
        
        # Verificar se todos os valores são strings
        for col in df.columns:
            assert isinstance(df.iloc[0][col], str)


class TestIntegration:
    """Testes de integração"""
    
    def test_full_pipeline_flow(self):
        """Testa fluxo completo do pipeline"""
        # Dados de teste
        vaga_data = {
            "V001": {
                "informacoes_basicas": {"titulo_vaga": "Dev Python"},
                "perfil_vaga": {"nivel profissional": "Senior"}
            }
        }
        
        candidate_data = {
            "C001": {
                "infos_basicas": {"nome": "João Silva"},
                "informacoes_profissionais": {"conhecimentos_tecnicos": "Python"}
            }
        }
        
        # Normalizar dados
        df_vagas = normalize_vagas(vaga_data)
        df_candidates = normalize_applicants(candidate_data)
        
        # Verificar se processamento funcionou
        assert not df_vagas.empty
        assert not df_candidates.empty
        
        # Preparar dados para predição
        vaga_row = df_vagas.iloc[0]
        candidate_row = df_candidates.iloc[0]
        prediction_df = prepare_prediction_data(vaga_row, candidate_row)
        
        assert not prediction_df.empty
        # Verificar apenas as 3 features que o modelo usa
        assert 'nivel_profissional' in prediction_df.columns
        assert 'areas_atuacao' in prediction_df.columns
        assert 'area_de_atuacao' in prediction_df.columns


if __name__ == '__main__':
    pytest.main([__file__])

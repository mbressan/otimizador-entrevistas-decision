import pytest
import json
import pandas as pd
import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app import app, prepare_hired_candidates_features

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
        "titulo_vaga": "Desenvolvedor Python Sênior",
        "competencias_tecnicas_requeridas": "Python, Django, FastAPI, PostgreSQL",
        "nivel_academico": "superior",
        "nivel_ingles": "intermediário",
        "nivel_profissional": "sênior",
        "tipo_contratacao": "clt",
        "areas_atuacao": "Tecnologia"
    }

@pytest.fixture
def sample_candidate():
    """Fixture com dados de exemplo de um candidato"""
    return {
        "conhecimentos_tecnicos": "Python, Django, PostgreSQL, Docker",
        "nivel_academico": "superior",
        "nivel_ingles": "avançado",
        "area_de_atuacao": "Desenvolvimento de Software"
    }

class TestFeaturePreparation:
    """Testes para a função de preparação de features."""

    def test_prepare_features_success(self, sample_vaga, sample_candidate):
        """Testa se a preparação de features ocorre com sucesso."""
        df = prepare_hired_candidates_features(sample_vaga, sample_candidate)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) == 1

    def test_feature_columns(self, sample_vaga, sample_candidate):
        """Verifica se todas as colunas esperadas são criadas."""
        df = prepare_hired_candidates_features(sample_vaga, sample_candidate)
        expected_columns = [
            'tech_success_score', 'academic_success_score', 'english_success_score',
            'is_clt', 'is_pj', 'is_tech_area', 'nivel_profissional',
            'areas_atuacao', 'area_atuacao_candidato', 'combined_text'
        ]
        for col in expected_columns:
            assert col in df.columns

    def test_missing_data_handling(self):
        """Testa o tratamento de dados ausentes ou vazios."""
        vaga_vazia = {}
        candidato_vazio = {}
        df = prepare_hired_candidates_features(vaga_vazia, candidato_vazio)
        assert not df.isnull().values.any()
        assert df.iloc[0]['tech_success_score'] == 0.5
        assert df.iloc[0]['academic_success_score'] == 1.0 # Default behavior based on logic
        assert df.iloc[0]['english_success_score'] == 1.0 # Default behavior based on logic
        assert df.iloc[0]['is_clt'] == 0
        assert df.iloc[0]['is_pj'] == 0
        assert df.iloc[0]['is_tech_area'] == 0
        assert df.iloc[0]['nivel_profissional'] == 'não_informado'

class TestFlaskRoutes:
    """Testes para as rotas da aplicação Flask."""

    def test_health_endpoint(self, client):
        """Testa o endpoint de health check."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['model_loaded'] is True

    def test_index_route(self, client):
        """Testa a rota principal."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"Otimizador de Entrevistas" in response.data

    def test_status_route(self, client):
        """Testa a rota de status."""
        response = client.get('/status')
        assert response.status_code == 200
        assert b"Status do Sistema" in response.data

    def test_predict_simple_api_success(self, client, sample_vaga, sample_candidate):
        """Testa o endpoint /api/predict_simple com dados válidos."""
        payload = {"vaga": sample_vaga, "candidato": sample_candidate}
        response = client.post('/api/predict_simple', json=payload)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'prediction' in data
        assert 'prediction_text' in data
        assert 'quality_score' in data
        assert 'analysis' in data
        assert 'tech_compatibility' in data['analysis']

    def test_predict_api_success(self, client, sample_vaga, sample_candidate):
        """Testa o endpoint /api/predict com dados válidos."""
        payload = {"vaga": sample_vaga, "candidato": sample_candidate}
        response = client.post('/api/predict', json=payload)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'prediction' in data
        assert 'prediction_text' in data
        assert 'match_score' in data
        assert 'explanation' in data
        assert 'tech_compatibility' in data['explanation']

    def test_predict_api_missing_data(self, client):
        """Testa a API de predição com dados faltando."""
        response = client.post('/api/predict_simple', json={"vaga": {}})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'Dados da vaga e candidato são obrigatórios'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

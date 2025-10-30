import pytest
from rest_framework.test import APIClient
from rest_framework import status
from busca_cep.models import Endereco
from unittest.mock import patch # Importa patch para mockar requests

@pytest.mark.django_db
class TestBuscaCEPView:

    def test_busca_cep_existente_no_banco(self):
        """Testa busca de CEP que já está salvo no banco (cache hit)."""
        # Arrange: Cria um endereço no banco
        cep_existente = "12345678"
        Endereco.objects.create(
            cep=cep_existente,
            logradouro="Rua do Banco",
            bairro="Bairro do Banco",
            localidade="Cidade do Banco",
            uf="BB",
            dados_historicos="Info do banco."
        )

        # Act: Faz a requisição
        client = APIClient()
        response = client.get(f'/api/cep/{cep_existente}/')

        # Assert: Verifica a resposta
        assert response.status_code == status.HTTP_200_OK
        assert response.data['cep'] == cep_existente
        assert response.data['logradouro'] == "Rua do Banco"
        assert response.data['dados_historicos'] == "Info do banco."

    def test_busca_cep_novo_com_sucesso(self, mocker):
        """Testa busca de CEP novo, que consulta a API externa e salva."""
        # Arrange: Dados que a API externa deve retornar
        cep_novo = "87654321"
        dados_correios = {
            "cep": "87654-321",
            "logradouro": "Rua Nova",
            "complemento": "Casa",
            "bairro": "Bairro Novo",
            "localidade": "São Paulo",
            "uf": "SP",
            "ibge": "3550308",
            "gia": "1004",
            "ddd": "11",
            "siafi": "7107"
        }

        # Mock da chamada para requests.get (Correios)
        with patch('busca_cep.views.requests.get') as mock_requests:
            mock_requests.return_value.status_code = 200
            mock_requests.return_value.json.return_value = dados_correios

            # Act: Faz a requisição
            client = APIClient()
            response = client.get(f'/api/cep/{cep_novo}/')

            # Assert: Verifica a resposta e persistência
            assert response.status_code == status.HTTP_200_OK
            assert response.data['cep'] == cep_novo
            assert response.data['logradouro'] == dados_correios['logradouro']
            # dados_historicos deve ser None, pois não chamamos Gemini (nem temos a lógica)
            assert response.data['dados_historicos'] is None

            # Verifica se o endereço foi salvo no banco
            endereco_salvo = Endereco.objects.get(cep=cep_novo)
            assert endereco_salvo.logradouro == dados_correios['logradouro']
            assert endereco_salvo.dados_historicos is None


    def test_busca_cep_nao_encontrado_na_api(self, mocker):
        """Testa busca de CEP que não existe na API externa."""
        # Arrange: Define o CEP e os dados simulando erro da API
        cep_inexistente = "99999999"
        dados_erro = {"erro": True}

        # Mock da chamada para requests.get
        with patch('busca_cep.views.requests.get') as mock_requests:
            mock_requests.return_value.status_code = 200 # A API dos Correios retorna 200 mesmo com erro
            mock_requests.return_value.json.return_value = dados_erro

            # Act: Faz a requisição
            client = APIClient()
            response = client.get(f'/api/cep/{cep_inexistente}/')

            # Assert: Verifica a resposta de erro
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert response.data['error'] == "CEP não encontrado."

            # Verifica que o CEP NÃO foi salvo no banco
            assert not Endereco.objects.filter(cep=cep_inexistente).exists()


    def test_busca_cep_invalido(self):
        """Testa busca de CEP inválido (formato incorreto)."""
        # Arrange: Define um CEP inválido
        cep_invalido = "12345" # Menos de 8 dígitos

        # Act: Faz a requisição
        client = APIClient()
        response = client.get(f'/api/cep/{cep_invalido}/')

        # Assert: Verifica a resposta de erro de validação
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['error'] == "CEP inválido. Deve conter 8 dígitos numéricos."

        # Verifica que o CEP NÃO foi salvo no banco
        assert not Endereco.objects.filter(cep=cep_invalido).exists()
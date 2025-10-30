from typing import Union, Dict, Optional
import requests
from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from busca_cep.models import Endereco
from busca_cep.serializers import EnderecoSerializer

# Definindo um tipo para os dados do CEP vindo da API dos Correios
DadosCorreios = Dict[str, Union[str, bool, None]] # Adicionando None como possível tipo

def buscar_dados(cep: str) -> tuple[Optional[Endereco], bool]:
    """
    Busca um endereço no banco de dados.
    Retorna (endereco, encontrado) ou (None, False) se não encontrado.
    """
    try:
        endereco: Endereco = Endereco.objects.get(cep=cep)
        return endereco, True
    except Endereco.DoesNotExist:
        return None, False

class BuscaCEPView(APIView):
    """
    View para buscar endereço por CEP, usando cache no banco de dados.
    """

    def get(self, request: HttpRequest, cep: Optional[str] = None) -> Response:
        if cep is None:
            cep = request.query_params.get('cep', '').strip()

        if not cep or len(cep) != 8 or not cep.isdigit():
            return Response(
                {"error": "CEP inválido. Deve conter 8 dígitos numéricos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. TENTAR BUSCAR NO BANCO DE DADOS (CACHE)
        endereco, encontrado = buscar_dados(cep)

        if encontrado:
            # Se encontrou no banco, retorna os dados do banco
            serializer = EnderecoSerializer(endereco)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 2. SE NÃO EXISTIR NO BANCO, FAZER A REQUISIÇÃO PARA OS CORREIOS
        url_correios: str = f"https://viacep.com.br/ws/{cep}/json/" # Corrigido: removido espaço extra

        try:
            response_correios = requests.get(url_correios)
            response_correios.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para os Correios: {e}")
            return Response(
                {"error": "Erro ao consultar o serviço dos Correios."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        dados_correios: DadosCorreios = response_correios.json()

        if dados_correios.get("erro"):
            return Response(
                {"error": "CEP não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. SE ACHAR NA API DOS CORREIOS, SALVAR NO BANCO E RETORNAR
        # Preparar os dados para o modelo
        dados_modelo: Dict[str, Optional[str]] = {
            'cep': dados_correios['cep'].replace('-', ''), # Garante o formato sem hífen
            'logradouro': dados_correios['logradouro'],
            'complemento': dados_correios['complemento'] or None,
            'bairro': dados_correios['bairro'],
            'localidade': dados_correios['localidade'],
            'uf': dados_correios['uf'],
            # 'dados_historicos': None # Opcional: definir explicitamente como None
        }

        endereco_novo: Endereco = Endereco.objects.create(**dados_modelo)
        # Serializar e retornar o objeto recém-criado
        serializer: EnderecoSerializer = EnderecoSerializer(endereco_novo)
        return Response(serializer.data, status=status.HTTP_200_OK)
from rest_framework import serializers
from .models import Endereco

class EnderecoSerializer(serializers.ModelSerializer[Endereco]):
    class Meta:
        model = Endereco
        fields = ['cep', 'logradouro',
                  'complemento',
                  'bairro',
                  'localidade',
                  'uf',
                  'data_atualizacao',
                  'dados_historicos']
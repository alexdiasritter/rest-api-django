from django.db import models

class Endereco(models.Model):
    cep = models.CharField(max_length=9, unique=True, primary_key=True)
    logradouro = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=255)
    localidade = models.CharField(max_length=255) # cidade
    uf = models.CharField(max_length=2) # estado
    data_atualizacao = models.DateTimeField(auto_now=True)
    dados_historicos = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f"{self.cep} - {self.logradouro}, {self.localidade}/{self.uf}"

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
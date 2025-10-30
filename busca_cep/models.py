from django.db import models

class Endereco(models.Model):
    cep = models.CharField(max_length=9, unique=True, primary_key=True)
    logradouro = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=255)
    localidade = models.CharField(max_length=255) # cidade
    uf = models.CharField(max_length=2) # estado
    # Podemos adicionar um campo de timestamp para controle de cache
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cep} - {self.logradouro}, {self.localidade}/{self.uf}"

    class Meta:
        verbose_name = "Endereço"
        verbose_name_plural = "Endereços"
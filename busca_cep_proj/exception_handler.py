from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Handler customizado para capturar e formatar exceções da API.
    """
    # Chama o handler padrão do DRF primeiro para obter a resposta padrão
    response = exception_handler(exc, context)

    # Se o DRF já gerou uma resposta (ex: validação de serializador),
    # apenas a retorna.
    if response is not None:
        return response

    logger.error(f"Exceção não tratada: {exc}", exc_info=True)

    # Retorna uma resposta de erro genérica e padronizada
    return Response(
        {"error": "Ocorreu um erro interno no servidor."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
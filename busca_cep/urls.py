from django.urls import path
from . import views

urlpatterns = [
    path('cep/<str:cep>/', views.BuscaCEPView.as_view(), name='buscar_cep'),
    # path('cep/', views.BuscaCEPView.as_view(), name='buscar_cep_query'), # Para ?cep=...
]
from django.urls import path
from .views import (
    index,
    register_view,
    insercao,
    insercao_mats,
    insercao_props,
    revisao_dados_view,
    calcular_view,
    resultados_view,
    under_construction,
    contact,
    contact_thanks,
)

urlpatterns = [
    # Home / Dashboard
    path('',                    index,                name='index'),

    # Cadastro
    path('register/',           register_view,        name='register'),

    # Fluxo do Formulário
    path('insercao/',           insercao,             name='insercao'),
    path('insercao/mats/',      insercao_mats,        name='insercao_mats'),
    path('insercao/props/',     insercao_props,       name='insercao_props'),

    # Página de revisão de dados
    path('revisao/',            revisao_dados_view,   name='revisao'),

    # Rota para executar o cálculo
    path('calcular/',           calcular_view,        name='calcular'),

    # Rota para exibir os resultados finais
    path('resultados/',         resultados_view,      name='resultados'),

    # Página em construção
    path('under-construction/', under_construction,    name='under_construction'),

    # Formulário de contato
    path('contact/',            contact,              name='contact'),

    # Página de agradecimento após contato
    path('contact/thanks/',     contact_thanks,       name='contact_thanks'),
]
